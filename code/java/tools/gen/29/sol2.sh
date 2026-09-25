cat > Sol2.java <<'EOF'
public class Sol2 {
    public static void main(String[] args) {
        String url = "x onclick=steal()";

        System.out.println("the value: " + url);
        System.out.println();
        System.out.println("escaped, it comes back unchanged:");
        System.out.println("  " + Html.escape(url));
        System.out.println();
        System.out.println("in an unquoted attribute:");
        System.out.println("  <a href=" + Html.escape(url) + ">x</a>");
        System.out.println();
        System.out.println("in a quoted attribute:");
        System.out.println("  <a href=\"" + Html.escape(url) + "\">x</a>");
        System.out.println();
        System.out.println("escaping cannot repair an unquoted attribute, because a space ends the");
        System.out.println("value and a space is not one of the five characters. Quoting it is the fix");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
