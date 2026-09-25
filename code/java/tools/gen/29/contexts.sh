cat > Contexts.java <<'EOF'
public class Contexts {
    static final String VALUE = "\" onmouseover=\"steal()";

    public static void main(String[] args) {
        String angleOnly = Html.escapeOnly(VALUE, "<>");
        String full = Html.escape(VALUE);

        System.out.println("the value: " + VALUE);
        System.out.println();
        System.out.println("element text, escaping < and > only:");
        System.out.println("  <p>" + angleOnly + "</p>");
        System.out.println("attribute value, escaping < and > only:");
        System.out.println("  <a title=\"" + angleOnly + "\">x</a>");
        System.out.println("attribute value, escaping all five:");
        System.out.println("  <a title=\"" + full + "\">x</a>");
        System.out.println();
        System.out.println("the quote closes the attribute, so everything after it is markup again");
        System.out.println("escaping < and > is enough for element text and not for an attribute");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Contexts.java
java -cp out Contexts
