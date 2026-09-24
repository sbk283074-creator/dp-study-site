public class Resources {

    static final class Handle implements AutoCloseable {
        private final String name;

        Handle(String name) {
            this.name = name;
            System.out.println("open " + name);
        }

        String use() {
            return "used " + name;
        }

        @Override
        public void close() {
            System.out.println("close " + name);
        }
    }

    public static void main(String[] args) {
        try (Handle first = new Handle("a"); Handle second = new Handle("b")) {
            System.out.println(first.use());
            System.out.println(second.use());
        }
        System.out.println("close ran before this line, in reverse order");
    }
}
