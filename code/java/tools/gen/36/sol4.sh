cat > Sol4.java <<'JAVA'
public class Sol4 {
    public static void main(String[] args) {
        Suite suite = new Suite();
        suite.add("a test that never runs its assertion", a -> {
            a.equal(1, 1, "this passes and proves nothing");
        });
        suite.add("a test that can fail", a -> {
            a.throwsWith(IllegalStateException.class,
                    () -> {
                        throw new IllegalStateException("closed");
                    },
                    "a closed store throws, and the test fails if it stops doing so");
        });
        int failed = suite.run();
        System.out.println();
        System.out.println("the difference between the two is the only thing that separates a");
        System.out.println("suite from a ritual: " + failed + " failure(s) here, and the second");
        System.out.println("test would catch it if the exception ever stopped being thrown");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
