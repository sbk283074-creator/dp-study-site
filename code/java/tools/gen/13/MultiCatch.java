public class MultiCatch {

    static String classify(String text) {
        try {
            int value = Integer.parseInt(text);
            return "number " + (100 / value);
        } catch (NumberFormatException | ArithmeticException e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
    }

    public static void main(String[] args) {
        System.out.println(classify("5"));
        System.out.println(classify("abc"));
        System.out.println(classify("0"));
        System.out.println("one block handled both kinds");
    }
}
