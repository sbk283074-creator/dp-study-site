cat > Sol1.java <<'EOF'
public class Sol1 {
    public static void main(String[] args) {
        String deep = "[".repeat(100000) + "]".repeat(100000);
        System.out.println("a body of " + deep.length() + " character(s):");

        System.out.println();
        System.out.println("with no limit:");
        try {
            JsonParser.parse(deep);
        } catch (StackOverflowError e) {
            System.out.println("  StackOverflowError, which the dispatcher cannot catch");
        }

        System.out.println();
        System.out.println("with a limit of 64:");
        try {
            JsonParser.parse(deep, 64);
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }

        System.out.println();
        System.out.println("the limit is one int checked in one place, and it belongs to the parser");
        System.out.println("rather than to the caller, so no route can forget to pass it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
