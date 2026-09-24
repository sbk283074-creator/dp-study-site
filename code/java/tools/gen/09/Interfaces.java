public class Interfaces {
    interface Named {
        String name();

        default String greeting() {
            return "I am " + name();
        }
    }

    interface Sized {
        int size();
    }

    static final class TextFile implements Named, Sized {
        private final String path;

        TextFile(String path) {
            this.path = path;
        }

        @Override
        public String name() {
            return path;
        }

        @Override
        public int size() {
            return path.length();
        }
    }

    static final class Person implements Named {
        private final String full;

        Person(String full) {
            this.full = full;
        }

        @Override
        public String name() {
            return full;
        }

        @Override
        public String greeting() {
            return "Hello, " + name();
        }
    }

    public static void main(String[] args) {
        Named[] things = {new TextFile("notes.txt"), new Person("Ada Lovelace")};
        for (Named thing : things) {
            System.out.println(thing.greeting());
        }

        Sized sized = new TextFile("notes.txt");
        System.out.println("size through the second interface: " + sized.size());

        System.out.println("TextFile implements both interfaces: "
                + (sized instanceof TextFile) + " and " + (sized instanceof Named));
        System.out.println("Person kept the default greeting: "
                + new Person("Ada").greeting().startsWith("Hello"));
    }
}
