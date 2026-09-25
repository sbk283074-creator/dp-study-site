cat > Sol3.java <<'EOF'
public class Sol3 {
    static final String[] BAD = {"javascript:", "data:", "vbscript:"};

    /** The instinct: list the schemes you have heard of, and refuse those. */
    static boolean looksSafe(String url) {
        for (String bad : BAD) {
            if (url.startsWith(bad)) {
                return false;
            }
        }
        return true;
    }

    public static void main(String[] args) {
        String[] urls = {
            "/notes/7",
            "javascript:steal()",
            "JavaScript:steal()",
            "jAvAsCrIpT:steal()",
            "data:text/html,<script>steal()</script>",
            "notes:7",
        };

        System.out.printf("%-42s %-10s %s%n", "url", "denylist", "allowlist");
        for (String url : urls) {
            System.out.printf("%-42s %-10s %s%n", "'" + url + "'",
                    looksSafe(url) ? "yes" : "NO",
                    Url.isSafe(url) ? "yes" : "NO");
        }

        System.out.println();
        System.out.println("the denylist catches the two it was written for and nothing else; the");
        System.out.println("allowlist refuses all five it does not recognise, because it fails closed");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
