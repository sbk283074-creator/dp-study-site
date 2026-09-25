cat > Script.java <<'EOF'
public class Script {
    static final String DATA = "{\"note\":\"</script>\"}";

    public static void main(String[] args) {
        System.out.println("the data the page hands to JavaScript:");
        System.out.println("  " + DATA);
        System.out.println();
        System.out.println("1. written raw into a script block:");
        System.out.println("  <script>const data = " + DATA + ";</script>");
        System.out.println();
        System.out.println("2. HTML-escaped first:");
        System.out.println("  <script>");
        System.out.println("  const data = " + Html.escape(DATA) + ";");
        System.out.println("  </script>");
        System.out.println();
        System.out.println("3. escaped the way JavaScript reads it:");
        System.out.println("  <script>");
        System.out.println("  const data = " + DATA.replace("<", "\\u003c") + ";");
        System.out.println("  </script>");
        System.out.println();
        System.out.println("inside <script> the HTML parser does not decode entities, so (2) is safe");
        System.out.println("and wrong -- the script receives the text &lt;/script&gt; and breaks");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Script.java
java -cp out Script
