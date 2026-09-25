cat > Sol1.java <<'EOF'
import java.util.HashMap;
import java.util.Map;

public class Sol1 {
    static final String STORED = "Ben & Jerry's";

    public static void main(String[] args) {
        System.out.println("the value in the database: " + STORED);
        System.out.println();
        System.out.println("the handler escapes, then the template escapes:");
        System.out.println("  " + Template.of("{{name}}").render(escapedByHandler()));
        System.out.println();
        System.out.println("only the template escapes:");
        System.out.println("  " + Template.of("{{name}}").render(plain()));
        System.out.println();
        System.out.println("both are safe and only one is right: the first shows the reader");
        System.out.println("&amp;amp; where the value was an ampersand, so escaping belongs at the");
        System.out.println("last moment, in the one place that writes markup");
    }

    static Map<String, String> escapedByHandler() {
        Map<String, String> values = new HashMap<>();
        values.put("name", Html.escape(STORED));
        return values;
    }

    static Map<String, String> plain() {
        Map<String, String> values = new HashMap<>();
        values.put("name", STORED);
        return values;
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
