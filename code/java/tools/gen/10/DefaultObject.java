public class DefaultObject {

    static final class Tag {
        final String label;

        Tag(String label) {
            this.label = label;
        }
    }

    public static void main(String[] args) {
        Tag a = new Tag("invoice");
        Tag b = new Tag("invoice");
        Tag c = a;

        String rendered = a.toString();

        System.out.println("the same reference equals itself: " + a.equals(c));
        System.out.println("a different object with the same label: " + a.equals(b));
        System.out.println("Object.equals is identity, nothing more: " + (a.equals(c) && !a.equals(b)));
        System.out.println("toString begins with the class name: "
                + rendered.startsWith("DefaultObject$Tag@"));
        System.out.println("toString ends with hex digits: "
                + rendered.substring(rendered.indexOf('@') + 1).matches("[0-9a-f]+"));
        System.out.println("printing an object calls toString: " + a.equals(a));
    }
}
