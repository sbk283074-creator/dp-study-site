public class ThisEscape {
    static class Base {
        private final String tag;

        Base() {
            tag = describe();
        }

        String describe() {
            return "base";
        }

        String tag() {
            return tag;
        }
    }

    static class Derived extends Base {
        // Deliberately not a compile-time constant. A literal here is a constant
        // variable, so javac folds it into describe() and the bug does not show.
        private final String id = new String("d");

        @Override
        String describe() {
            return "derived " + id;
        }
    }

    public static void main(String[] args) {
        Derived derived = new Derived();
        System.out.println("captured during construction: [" + derived.tag() + "]");
        System.out.println("the same call afterwards:     [" + derived.describe() + "]");
        System.out.println("the subclass field was still null when super() called the override");
    }
}
