import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** The smallest thing that can fail loudly: a counter and a list of what broke. */
public final class Assert {

    private final List<String> failures = new ArrayList<>();
    private int checks;

    public void that(boolean condition, String what) {
        checks++;
        if (!condition) {
            failures.add(what);
        }
    }

    public void equal(Object expected, Object actual, String what) {
        checks++;
        if (!Objects.equals(expected, actual)) {
            failures.add(what + " (expected " + expected + ", got " + actual + ")");
        }
    }

    public void throwsWith(Class<?> type, Runnable body, String what) {
        checks++;
        try {
            body.run();
            failures.add(what + " (nothing was thrown)");
        } catch (RuntimeException e) {
            if (!type.isInstance(e)) {
                failures.add(what + " (threw " + e.getClass().getSimpleName() + ")");
            }
        }
    }

    public int checks() {
        return checks;
    }

    public int failures() {
        return failures.size();
    }

    public List<String> problems() {
        return failures;
    }
}
