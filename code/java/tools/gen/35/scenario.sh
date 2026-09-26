cat > Scenario.java <<'JAVA'
import java.util.List;
import java.util.Map;

public class Scenario {
    public static void main(String[] args) {
        Config config = new Config();
        config.layer(Map.of("port", "8080", "level", "info", "db", "bulletin.db"),
                "defaults");
        config.layer(Map.of("db", ""), "environment");
        config.layer(Map.of("token", "abc123"), "environment");

        List<String> problems = config.validate();
        System.out.println("--- a deploy with an empty DB_URL set in the environment ---");
        System.out.println("  problems found : " + problems.size());
        for (String problem : problems) {
            System.out.println("  " + problem);
        }
        System.out.println();
        System.out.println("  and the token never appears in any of that output:");
        System.out.println("  " + config.printed());
        System.out.println();
        System.out.println("this is what startup validation is for: the process dies here,");
        System.out.println("before it binds a port, before it serves a request, and with a");
        System.out.println("message that names the variable somebody set wrong");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
