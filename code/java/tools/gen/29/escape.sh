cat > Escape.java <<'EOF'
public class Escape {
    public static void main(String[] args) {
        String[] characters = {"&", "<", ">", "\"", "'"};
        String[] names = {"ampersand", "less than", "greater than", "double quote", "single quote"};

        for (int i = 0; i < characters.length; i++) {
            System.out.printf("%-14s -> %s%n", names[i], Html.escape(characters[i]));
        }

        System.out.println();
        String tricky = "&lt;script&gt;";
        System.out.println("the text          : " + tricky);
        System.out.println("escaped           : " + Html.escape(tricky));
        System.out.println("and escaped again : " + Html.escape(Html.escape(tricky)));
        System.out.println();
        System.out.println("the second escape is the bug that ships: a value that was already escaped");
        System.out.println("has its ampersands escaped, and the reader is shown &amp;lt; instead of <");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Escape.java
java -cp out Escape
