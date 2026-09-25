import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;

public class MiniTest {
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface Test {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface BeforeEach {}

    public static class AssertionFailure extends RuntimeException {
        private static final long serialVersionUID = 1L;

        AssertionFailure(String message) {
            super(message);
        }
    }

    public record Result(String name, boolean passed, String detail) {}

    static void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionFailure("expected <" + expected + "> but was <" + actual + ">");
        }
    }

    public static List<Result> run(Class<?> suite) throws ReflectiveOperationException {
        List<Method> tests = new ArrayList<>();
        List<Method> befores = new ArrayList<>();
        for (Method m : suite.getDeclaredMethods()) {
            if (m.isAnnotationPresent(Test.class)) {
                tests.add(m);
            } else if (m.isAnnotationPresent(BeforeEach.class)) {
                befores.add(m);
            }
        }
        tests.sort(Comparator.comparing(Method::getName));
        befores.sort(Comparator.comparing(Method::getName));

        List<Result> results = new ArrayList<>();
        for (Method test : tests) {
            Object instance = suite.getDeclaredConstructor().newInstance();
            try {
                for (Method before : befores) {
                    before.invoke(instance);
                }
                test.invoke(instance);
                results.add(new Result(test.getName(), true, ""));
            } catch (InvocationTargetException e) {
                Throwable cause = e.getCause();
                results.add(new Result(test.getName(), false,
                        cause.getClass().getSimpleName() + ": " + cause.getMessage()));
            }
        }
        return results;
    }

    public static void report(Class<?> suite, List<Result> results) {
        int passed = 0;
        for (Result r : results) {
            if (r.passed()) {
                passed++;
                System.out.printf("PASS  %s%n", r.name());
            } else {
                System.out.printf("FAIL  %s  <- %s%n", r.name(), r.detail());
            }
        }
        System.out.printf("%s: %d of %d passed%n", suite.getSimpleName(), passed, results.size());
    }

    static class Suite {
        private int calls;

        @BeforeEach
        void freshState() {
            calls = 0;
        }

        @Test
        void adds() {
            calls++;
            assertEquals(4, 2 + 2);
            assertEquals(1, calls);
        }

        @Test
        void counts() {
            calls += 2;
            assertEquals(2, calls);
        }

        @Test
        void fails() {
            assertEquals(5, 2 + 2);
        }
    }

    public static void main(String[] args) throws ReflectiveOperationException {
        report(Suite.class, run(Suite.class));
    }
}
