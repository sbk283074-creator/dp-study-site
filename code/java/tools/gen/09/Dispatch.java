public class Dispatch {
    static class Base {
        String label = "base field";

        String label() {
            return "base method";
        }

        String report() {
            return "report sees " + label() + " and " + label;
        }
    }

    static class Derived extends Base {
        String label = "derived field";

        @Override
        String label() {
            return "derived method";
        }
    }

    public static void main(String[] args) {
        Base asBase = new Derived();
        Derived asDerived = new Derived();

        System.out.println("through a Base reference:");
        System.out.println("  " + asBase.report());
        System.out.println("  asBase.label() = " + asBase.label());
        System.out.println("  asBase.label   = " + asBase.label);

        System.out.println("through a Derived reference:");
        System.out.println("  " + asDerived.report());
        System.out.println("  asDerived.label() = " + asDerived.label());
        System.out.println("  asDerived.label   = " + asDerived.label);

        Base[] items = {new Base(), new Derived()};
        for (Base item : items) {
            System.out.println("  a Base[] holds both and calls " + item.label());
        }
        System.out.println("methods dispatch on the object; fields are read from the reference type");
    }
}
