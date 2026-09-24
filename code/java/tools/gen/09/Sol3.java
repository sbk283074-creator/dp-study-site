import java.util.Locale;

public class Sol3 {
    interface Greeter {
        String name();

        default String greet() {
            return "Hello, " + name();
        }

        default String shout() {
            return greet().toUpperCase(Locale.ROOT) + "!";
        }
    }

    static final class Plain implements Greeter {
        @Override
        public String name() {
            return "world";
        }
    }

    static final class Formal implements Greeter {
        @Override
        public String name() {
            return "Dr. Chen";
        }

        @Override
        public String greet() {
            return "Good morning, " + name();
        }
    }

    public static void main(String[] args) {
        Greeter[] greeters = {new Plain(), new Formal()};
        for (Greeter greeter : greeters) {
            System.out.println(greeter.greet() + "   /   " + greeter.shout());
        }
        System.out.println("shout() is inherited by both and builds on whichever greet() they have");
    }
}
