cat > Doubles.java <<'JAVA'
import java.util.ArrayList;
import java.util.List;

public class Doubles {
    public static void main(String[] args) {
        Clock clock = new Clock();
        long start = clock.now();
        List<String> log = new ArrayList<>();

        Session session = new Session(clock, 60_000L, log);
        System.out.println("at the start   : " + session.state());
        clock.advance(60_000L);
        System.out.println("after a minute : " + session.state());
        System.out.println("and the clock advanced by exactly " + (clock.now() - start) + " ms");
        System.out.println();
        System.out.println("the test decided when a minute passed, so it did not take one.");
        System.out.println("A session tested against the real clock either waits sixty");
        System.out.println("seconds or does not test the boundary at all");

        System.out.println();
        log.add("expired");
        System.out.println("the fake also recorded: " + log);
        System.out.println("which is what a test double is for: not to imitate the thing,");
        System.out.println("but to make the thing observable");
    }

    static final class Session {
        private final Clock clock;
        private final long deadline;
        private final List<String> log;

        Session(Clock clock, long lifetimeMillis, List<String> log) {
            this.clock = clock;
            this.deadline = clock.now() + lifetimeMillis;
            this.log = log;
        }

        String state() {
            return clock.expired(deadline) ? "expired" : "alive";
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Doubles.java
java -cp out Doubles
