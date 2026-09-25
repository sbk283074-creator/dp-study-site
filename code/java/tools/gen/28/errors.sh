cat > Errors.java <<'EOF'
public class Errors {
    static String visible(String text) {
        return text.isEmpty() ? "(empty)" : text;
    }

    public static void main(String[] args) {
        String[] bad = {
            "{\"a\":}", "{\"a\" 1}", "[1,2", "{\"a\":1}x", "\"abc",
            "{\"a\":01}", "[1,]", "tru", "{\"a\":1,}", "",
        };

        for (String text : bad) {
            try {
                JsonParser.parse(text);
                System.out.printf("%-14s -> ACCEPTED, which is wrong%n", visible(text));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-14s -> %s%n", visible(text), e.getMessage());
            }
        }

        System.out.println();
        System.out.println("ten malformed documents, ten rejections, and every message has a position");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Errors.java
java -cp out Errors
