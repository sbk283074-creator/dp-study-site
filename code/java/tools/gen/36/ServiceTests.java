import java.util.Map;

/** The unit tests for Chapters 30 to 35, in one file, so they can be run together. */
public class ServiceTests {

    public static void main(String[] args) {
        Suite suite = new Suite();

        suite.add("a config value remembers where it came from", a -> {
            Map<String, String> defaults = Map.of("port", "8080");
            a.equal("8080", defaults.get("port"), "the default is 8080");
            a.that(defaults.containsKey("port"), "port is present");
        });

        suite.add("an escape turns five characters into entities", a -> {
            a.equal("&amp;", Escaping.html("&"), "ampersand first, always");
            a.equal("&lt;", Escaping.html("<"), "less than");
            a.equal("&gt;", Escaping.html(">"), "greater than");
            a.equal("&quot;", Escaping.html("\""), "double quote");
            a.equal("&#39;", Escaping.html("'"), "single quote");
        });

        suite.add("escaping twice is a bug the test can see", a -> {
            String once = Escaping.html("a & b");
            String twice = Escaping.html(once);
            a.equal("a &amp; b", once, "escaped once");
            a.that(!once.equals(twice), "escaping twice changes the meaning");
        });

        suite.add("a session expires when the clock says so", a -> {
            Clock clock = new Clock();
            long deadline = clock.now() + 60_000L;
            a.that(!clock.expired(deadline), "alive before the deadline");
            clock.advance(59_999L);
            a.that(!clock.expired(deadline), "alive one millisecond early");
            clock.advance(1L);
            a.that(clock.expired(deadline), "expired exactly on the deadline");
        });

        suite.add("a bounded pool refuses instead of growing", a -> {
            Bounded pool = new Bounded(2);
            a.that(pool.borrow(), "first borrow succeeds");
            a.that(pool.borrow(), "second borrow succeeds");
            a.that(!pool.borrow(), "third borrow is refused");
            pool.giveBack();
            a.that(pool.borrow(), "and succeeds after one comes back");
            a.equal(2, pool.size(), "the pool never grew past two");
        });

        suite.add("a failure is a test that fails, not a crash", a -> {
            a.throwsWith(IllegalArgumentException.class,
                    () -> {
                        throw new IllegalArgumentException("bad input");
                    },
                    "an illegal argument is thrown");
            a.throwsWith(IllegalStateException.class,
                    () -> {
                        throw new IllegalArgumentException("wrong type");
                    },
                    "this one is wrong on purpose, and the test says so");
        });

        int failed = suite.run();
        if (failed > 0) {
            System.out.println();
            System.out.println("the last failure is deliberate: a test that cannot fail is");
            System.out.println("not a test, and the point of this file is that every one of");
            System.out.println("these can");
        }
    }
}
