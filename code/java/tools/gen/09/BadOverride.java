public class BadOverride {
    static class Base {
        String describe() {
            return "base";
        }
    }

    static class Derived extends Base {
        @Override
        String describe(int times) {
            return "derived";
        }
    }

    public static void main(String[] args) {
        System.out.println(new Derived().describe());
    }
}
