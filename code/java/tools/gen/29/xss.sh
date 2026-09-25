cat > Xss.java <<'EOF'
public class Xss {
    static final String PAYLOAD = "<img src=x onerror=steal()>";

    public static void main(String[] args) {
        System.out.println("what the comment field held:");
        System.out.println("  " + PAYLOAD);
        System.out.println();
        System.out.println("built by concatenation:");
        System.out.println("  <div class=\"comment\">" + PAYLOAD + "</div>");
        System.out.println();
        System.out.println("built through the template:");
        System.out.println("  <div class=\"comment\">" + Html.escape(PAYLOAD) + "</div>");
        System.out.println();
        System.out.println("the first document contains an img element and the second contains text");
        System.out.println("about an img element; the difference is one function call");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Xss.java
java -cp out Xss
