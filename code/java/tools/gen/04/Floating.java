import java.math.BigDecimal;

public class Floating {
    public static void main(String[] args) {
        double sum = 0.1 + 0.2;
        System.out.println("0.1 + 0.2        = " + sum);
        System.out.println("== 0.3           = " + (sum == 0.3));
        System.out.println("0.1f == 0.1      = " + (0.1f == 0.1));

        double third = 1.0 / 3.0;
        System.out.println("1.0 / 3.0        = " + third);
        System.out.println("(1.0/3.0) * 3.0  = " + (third * 3));

        BigDecimal exact = new BigDecimal("0.1").add(new BigDecimal("0.2"));
        System.out.println("BigDecimal       = " + exact);
        System.out.println("BigDecimal ==0.3 = " + (exact.compareTo(new BigDecimal("0.3")) == 0));

        System.out.println("(float) MAX_VALUE= " + (float) Integer.MAX_VALUE);
        System.out.println("NaN == NaN       = " + (Double.NaN == Double.NaN));
        System.out.println("isNaN(0.0 / 0.0) = " + Double.isNaN(0.0 / 0.0));
        System.out.println("1e308 * 10       = " + (1e308 * 10));
    }
}
