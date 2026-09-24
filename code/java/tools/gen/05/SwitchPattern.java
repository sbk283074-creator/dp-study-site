public class SwitchPattern {
    static String describe(Object value) {
        return switch (value) {
            case null -> "nothing at all";
            case Integer i when i < 0 -> "negative integer " + i;
            case Integer i -> "integer " + i;
            case String s when s.isBlank() -> "blank text";
            case String s -> "text of length " + s.length();
            case Double d -> "double " + d;
            default -> "some other " + value.getClass().getSimpleName();
        };
    }

    public static void main(String[] args) {
        Object[] samples = {null, -5, 42, "", "   ", "quill", 2.5, 7L};
        for (Object sample : samples) {
            System.out.println(describe(sample));
        }
        System.out.println("a guard runs before the arm it is attached to: "
                + describe(-1) + " / " + describe(1));
    }
}
