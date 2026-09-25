cat > Depth.java <<'EOF'
public class Depth {
    public static void main(String[] args) {
        for (int depth : new int[] {1000, 5000}) {
            String document = "[".repeat(depth) + "]".repeat(depth);
            System.out.printf("%6d levels, %6d characters -> ", depth, document.length());
            try {
                JsonParser.parse(document);
                System.out.println("parsed");
            } catch (StackOverflowError e) {
                System.out.println("StackOverflowError");
            }
        }

        System.out.println();
        System.out.println("a depth limit turns that into an ordinary refusal:");
        String deep = "[".repeat(5000) + "]".repeat(5000);
        try {
            JsonParser.parse(deep, 64);
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }

        System.out.println();
        System.out.println("StackOverflowError is an Error, not a RuntimeException, so Chapter 27's");
        System.out.println("catch (RuntimeException e) in the dispatcher does not catch it:");
        try {
            try {
                JsonParser.parse("[".repeat(100000) + "]".repeat(100000));
            } catch (RuntimeException e) {
                System.out.println("  caught as a RuntimeException");
            }
        } catch (StackOverflowError e) {
            System.out.println("  it escaped that catch and arrived as " + e.getClass().getName());
        }
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Depth.java
java -cp out Depth
