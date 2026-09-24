public class Suppressed {

    static final class Failing implements AutoCloseable {
        private final String name;

        Failing(String name) {
            this.name = name;
        }

        void fail() {
            throw new IllegalStateException("body failed");
        }

        @Override
        public void close() {
            throw new IllegalArgumentException(name + " close failed");
        }
    }

    public static void main(String[] args) {
        try {
            try (Failing resource = new Failing("file")) {
                resource.fail();
            }
        } catch (IllegalStateException e) {
            System.out.println("thrown from the body: " + e.getMessage());
            System.out.println("suppressed count: " + e.getSuppressed().length);
            System.out.println("suppressed: " + e.getSuppressed()[0].getMessage());
        }
    }
}
