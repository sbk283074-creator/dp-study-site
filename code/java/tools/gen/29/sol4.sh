cat > Sol4.java <<'EOF'
public class Sol4 {
    static final String INPUT = "nice <b>work</b> <script>steal()</script>";

    /** Escape everything, then un-escape the two tags that are allowed. */
    static String boldOnly(String text) {
        return Html.escape(text)
                .replace("&lt;b&gt;", "<b>")
                .replace("&lt;/b&gt;", "</b>");
    }

    public static void main(String[] args) {
        System.out.println("what the user typed:");
        System.out.println("  " + INPUT);
        System.out.println();
        System.out.println("through {{{ }}} -- every character is markup:");
        System.out.println("  " + INPUT);
        System.out.println();
        System.out.println("through {{ }} -- every character is text:");
        System.out.println("  " + Html.escape(INPUT));
        System.out.println();
        System.out.println("through a bold-only allowlist:");
        System.out.println("  " + boldOnly(INPUT));
        System.out.println();
        System.out.println("the raw marker cannot be made safe by inspecting the value, because the");
        System.out.println("value is unbounded. An allowlist is bounded by construction");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
