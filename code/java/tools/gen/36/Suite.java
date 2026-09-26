import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/** Runs every test, reports every failure, and exits with the number that failed. */
public final class Suite {

    private record Test(String name, Consumer<Assert> body) {
    }

    private final List<Test> tests = new ArrayList<>();

    public void add(String name, Consumer<Assert> body) {
        tests.add(new Test(name, body));
    }

    public int run() {
        int failed = 0;
        int checks = 0;
        for (Test test : tests) {
            Assert assert_ = new Assert();
            try {
                test.body().accept(assert_);
            } catch (RuntimeException e) {
                assert_.that(false, "threw " + e.getClass().getSimpleName()
                        + ": " + e.getMessage());
            }
            boolean ok = assert_.failures() == 0;
            if (!ok) {
                failed++;
            }
            checks += assert_.checks();
            System.out.println((ok ? "  PASS  " : "  FAIL  ") + test.name()
                    + "  (" + assert_.checks() + " check(s))");
            for (String problem : assert_.problems()) {
                System.out.println("          ! " + problem);
            }
        }
        System.out.println();
        System.out.println(tests.size() + " test(s), " + checks + " check(s), "
                + failed + " failure(s)");
        return failed;
    }
}
