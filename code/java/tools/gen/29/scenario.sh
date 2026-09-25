cat > Scenario.java <<'EOF'
import java.util.HashMap;
import java.util.Map;

public class Scenario {
    static final String ATTACK = "javascript:steal()";

    public static void main(String[] args) {
        String template = "<a href=\"{{url}}\">the link</a>";

        System.out.println("the template: " + template);
        System.out.println("the value:    " + ATTACK);
        System.out.println();
        System.out.println("rendered:");
        System.out.println("  " + render(template, ATTACK));
        System.out.println();
        System.out.println("the engine escaped every character it knows about:");
        System.out.println("  " + ATTACK + " -> " + Html.escape(ATTACK));
        System.out.println("which is to say it changed nothing at all");
        System.out.println();
        System.out.println("a scheme allowlist refuses the value:");
        System.out.println("  Url.isSafe(\"" + ATTACK + "\") = " + Url.isSafe(ATTACK));
    }

    static String render(String template, String value) {
        Map<String, String> values = new HashMap<>();
        values.put("url", value);
        return Template.of(template).render(values);
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
