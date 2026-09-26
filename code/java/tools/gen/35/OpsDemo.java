import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class OpsDemo {
    public static void main(String[] args) {
        Config config = new Config();

        Map<String, String> defaults = new LinkedHashMap<>();
        defaults.put("port", "8080");
        defaults.put("level", "info");
        defaults.put("db", "bulletin.db");
        defaults.put("secret", "from-defaults");
        config.layer(defaults, "defaults");

        Map<String, String> file = new LinkedHashMap<>();
        file.put("db", "/var/lib/bulletin/app.db");
        config.layer(file, "config file");

        Map<String, String> environment = new LinkedHashMap<>();
        environment.put("level", "debug");
        config.layer(environment, "environment");

        config.arguments(new String[]{"--port=9090", "--secret=s3cr3t"});

        System.out.println("--- where every value came from ---");
        for (String key : List.of("port", "level", "db", "secret")) {
            System.out.println("  " + key + " = " + config.get(key)
                    + "   (" + config.originOf(key) + ")");
        }
        System.out.println();
        System.out.println("four layers, last wins: arguments beat environment, which beats");
        System.out.println("the file, which beats the defaults. The point of recording the");
        System.out.println("origin is that `--print-config` then answers \"why is this value");
        System.out.println("what it is\" instead of only \"what is it\"");

        System.out.println();
        System.out.println("--- printed, with secrets removed ---");
        System.out.println("  " + config.printed());

        System.out.println();
        System.out.println("--- validation, before anything is served ---");
        List<String> problems = config.validate();
        System.out.println("  problems : " + problems.size());

        Config broken = new Config();
        broken.layer(Map.of("port", "0", "level", "loud"), "arguments");
        for (String problem : broken.validate()) {
            System.out.println("  " + problem);
        }

        System.out.println();
        System.out.println("--- log lines, numbered rather than timestamped ---");
        Log log = new Log("info");
        log.line("debug", "this is below the threshold and never appears");
        log.line("info", "server starting", "port", "9090");
        log.line("info", "login", "user", "bob", "password", "hunter2");
        log.line("warn", "slow request", "path", "/notes", "millis", "812");
        System.out.println("  written      : " + log.written());
        System.out.println("  debug kept   : " + log.enabled("debug"));

        System.out.println();
        System.out.println("--- a value that tries to forge a log line ---");
        log.line("info", "login", "user", "bob\nINJECTED admin=true");
        System.out.println();
        System.out.println("  the newline became \\n, so the value stayed one field and the");
        System.out.println("  line stayed one line. Without that, a username can write");
        System.out.println("  whatever it likes into your log aggregation");

        System.out.println();
        System.out.println("--- shutdown, in reverse order, once ---");
        Hooks hooks = new Hooks();
        hooks.add(() -> System.out.println("  stop accepting requests"));
        hooks.add(() -> System.out.println("  close the pool"));
        hooks.add(() -> System.out.println("  close the database"));
        hooks.run();
        hooks.run();
        System.out.println("  stopped      : " + hooks.stopped());
    }
}
