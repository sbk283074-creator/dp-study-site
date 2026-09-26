cat > Layering.java <<'JAVA'
import java.util.LinkedHashMap;
import java.util.Map;

public class Layering {
    public static void main(String[] args) {
        Config config = new Config();
        config.layer(Map.of("port", "8080", "level", "info"), "defaults");
        System.out.println("after defaults  : port=" + config.get("port")
                + " from " + config.originOf("port"));

        Map<String, String> file = new LinkedHashMap<>();
        file.put("port", "7000");
        config.layer(file, "config file");
        System.out.println("after the file  : port=" + config.get("port")
                + " from " + config.originOf("port"));

        config.layer(Map.of("port", "6000"), "environment");
        System.out.println("after env       : port=" + config.get("port")
                + " from " + config.originOf("port"));

        config.arguments(new String[]{"--port=5000"});
        System.out.println("after arguments : port=" + config.get("port")
                + " from " + config.originOf("port"));

        config.arguments(new String[]{"--port"});
        System.out.println("a flag with no = : port=" + config.get("port")
                + " from " + config.originOf("port"));
        System.out.println();
        System.out.println("the last layer to speak wins, and every value knows who spoke");
        System.out.println("last -- which is the difference between a config bug you can");
        System.out.println("see and one you have to reproduce");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Layering.java
java -cp out Layering
