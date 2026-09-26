cat > Sol2.java <<'JAVA'
public class Sol2 {
    public static void main(String[] args) {
        Clock clock = new Clock();
        long deadline = clock.now() + 1000L;
        System.out.println("before           : " + (clock.expired(deadline) ? "expired" : "alive"));
        clock.advance(999L);
        System.out.println("at 999 ms        : " + (clock.expired(deadline) ? "expired" : "alive"));
        clock.advance(1L);
        System.out.println("at 1000 ms       : " + (clock.expired(deadline) ? "expired" : "alive"));
        System.out.println();
        System.out.println("the boundary is a millisecond wide and the test can stand on it,");
        System.out.println("because the test owns the clock");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
