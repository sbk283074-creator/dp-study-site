cat > Schemes.java <<'EOF'
public class Schemes {
    public static void main(String[] args) {
        String[] urls = {
            "/notes/7",
            "notes/7",
            "https://example.com/a?b=1",
            "http://example.com",
            "mailto:lucas@example.com",
            "/notes?next=javascript:steal()",
            "/a:b",
            "notes:7",
            "javascript:steal()",
            "JavaScript:steal()",
            "  javascript:steal()",
            "data:text/html,<script>steal()</script>",
        };

        System.out.printf("%-44s %s%n", "url", "safe in an href?");
        for (String url : urls) {
            System.out.printf("%-44s %s%n", "'" + url + "'", Url.isSafe(url) ? "yes" : "NO");
        }

        System.out.println();
        System.out.println("the payload contains no character that HTML escaping touches:");
        System.out.println("  javascript:steal() -> " + Html.escape("javascript:steal()"));
        System.out.println();
        System.out.println("so escaping is not the defence here. A scheme allowlist is, and the");
        System.out.println("comparison has to ignore case, because URL schemes are case-insensitive");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Schemes.java
java -cp out Schemes
