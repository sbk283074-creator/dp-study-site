public class Division {
    public static void main(String[] args) {
        int a = 7, b = 2;
        System.out.println("7 / 2          = " + (a / b));
        System.out.println("7 % 2          = " + (a % b));
        System.out.println("7 / 2.0        = " + (7 / 2.0));

        int negative = -7;
        System.out.println("-7 / 2         = " + (negative / 2));
        System.out.println("-7 % 2         = " + (negative % 2));
        System.out.println("7 % -2         = " + (7 % -2));
        System.out.println("-7 % -2        = " + (negative % -2));

        double looksRight = 7 / 2;
        System.out.println("double d = 7/2 = " + looksRight);
        System.out.println("(double) 7 / 2 = " + ((double) 7 / 2));

        int zero = 0;
        try {
            System.out.println("7 / zero       = " + (7 / zero));
        } catch (ArithmeticException e) {
            System.out.println("7 / zero       : " + e.getMessage());
        }
        System.out.println("7.0 / zero     = " + (7.0 / zero));
        System.out.println("0.0 / zero     = " + (0.0 / zero));
        System.out.println("0 / 0.0        = " + (0 / 0.0));
    }
}
