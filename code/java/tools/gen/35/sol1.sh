cat > Sol1.java <<'JAVA'
import java.util.Map;

public class Sol1 {
    public static void main(String[] args) {
        Config config = new Config();
        config.layer(Map.of("port", "8080"), "defaults");
        config.layer(Map.of("port", "9090"), "environment");
        config.arguments(new String[]{"--port=7070"});
        System.out.println("port   : " + config.get("port"));
        System.out.println("origin : " + config.originOf("port"));
        System.out.println();
        System.out.println("arguments win, because they are applied last. A layer is just an");
        System.out.println("assignment plus a note about who made it");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
