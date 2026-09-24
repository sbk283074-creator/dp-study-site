public class Sol2 {

    static final class Counter implements AutoCloseable {
        private final String name;
        private int uses;

        Counter(String name) {
            this.name = name;
        }

        int next() {
            uses++;
            return uses;
        }

        @Override
        public void close() {
            System.out.println("closed " + name + " after " + uses + " use(s)");
        }
    }

    public static void main(String[] args) {
        try (Counter a = new Counter("a"); Counter b = new Counter("b")) {
            System.out.println("a -> " + a.next());
            System.out.println("b -> " + b.next());
            System.out.println("a -> " + a.next());
        }
        System.out.println("both are closed before this line runs");
    }
}
