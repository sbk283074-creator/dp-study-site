public class ExpectsThrow {
    static int divide(int a, int b) {
        return a / b;
    }

    static String assertThrows(Class<? extends Throwable> expected, Runnable body) {
        try {
            body.run();
        } catch (Throwable actual) {
            if (expected.isInstance(actual)) {
                return "threw " + actual.getClass().getSimpleName() + ": " + actual.getMessage();
            }
            return "wrong type: " + actual.getClass().getSimpleName();
        }
        return "nothing thrown";
    }

    public static void main(String[] args) {
        int numerator = 1;
        int denominator = 0;

        System.out.println("divide   = " + assertThrows(ArithmeticException.class,
                () -> divide(numerator, denominator)));
        System.out.println("parse    = " + assertThrows(NumberFormatException.class,
                () -> Integer.parseInt("nope")));
        System.out.println("mismatch = " + assertThrows(IllegalStateException.class,
                () -> divide(numerator, denominator)));
        System.out.println("silent   = " + assertThrows(ArithmeticException.class,
                () -> divide(numerator, numerator)));
    }
}
