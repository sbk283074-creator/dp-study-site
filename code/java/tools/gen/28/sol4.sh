cat > Sol4.java <<'EOF'
public class Sol4 {
    static String verdict(String body) {
        try {
            JsonParser.parse(body);
            return "accepted";
        } catch (IllegalArgumentException e) {
            return e.getMessage();
        }
    }

    public static void main(String[] args) {
        String[] bodies = {"{\"a\":1}", "{\"a\":1}   ", "{\"a\":1}x", "{\"a\":1}{\"b\":2}"};

        for (String body : bodies) {
            System.out.printf("%-24s -> %s%n", "'" + body + "'", verdict(body));
        }

        System.out.println();
        System.out.println("trailing whitespace is fine and a second value is not, because the check is");
        System.out.println("'the input ended', not 'the first value ended'. A parser that stopped at the");
        System.out.println("first value would accept the last body and drop {\"b\":2} without a word");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
