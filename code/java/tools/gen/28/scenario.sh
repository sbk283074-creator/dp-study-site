cat > Scenario.java <<'EOF'
public class Scenario {
    /** Chapter 27's dispatcher, in miniature: the catch is RuntimeException. */
    static String dispatch(String body) {
        try {
            Json parsed = JsonParser.parse(body);
            return "200 " + JsonWriter.write(parsed);
        } catch (RuntimeException e) {
            return "400 " + e.getMessage();
        }
    }

    public static void main(String[] args) {
        System.out.println("a malformed body:");
        System.out.println("  " + dispatch("{\"a\":}"));

        String deep = "[".repeat(100000) + "]".repeat(100000);
        System.out.println();
        System.out.println("a nested body of " + deep.length() + " character(s):");
        try {
            System.out.println("  " + dispatch(deep));
        } catch (StackOverflowError e) {
            System.out.println("  the dispatcher never returned: " + e.getClass().getName());
        }

        System.out.println();
        System.out.println("the dispatcher catches RuntimeException, and StackOverflowError is an");
        System.out.println("Error -- so it is not caught, and the client gets no response at all");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
