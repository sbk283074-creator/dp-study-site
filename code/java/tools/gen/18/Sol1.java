import java.math.BigDecimal;
import java.math.RoundingMode;

public class Sol1 {
    static BigDecimal money(String amount) {
        return new BigDecimal(amount).setScale(2, RoundingMode.HALF_UP);
    }

    public static void main(String[] args) {
        BigDecimal unit = money("19.995");
        System.out.println("rounded   = " + unit);
        System.out.println("equals    = " + unit.equals(new BigDecimal("20.00")));
        System.out.println("compareTo = " + (unit.compareTo(new BigDecimal("20.00")) == 0));

        BigDecimal total = unit.multiply(BigDecimal.valueOf(3));
        System.out.println("total     = " + total);

        BigDecimal split = total.divide(BigDecimal.valueOf(3), 2, RoundingMode.HALF_UP);
        System.out.println("split     = " + split);
        System.out.println("scale     = " + split.scale());

        BigDecimal ten = new BigDecimal("10.00");
        BigDecimal third = ten.divide(new BigDecimal("3"), 2, RoundingMode.HALF_UP);
        System.out.println("third     = " + third);
        System.out.println("three     = " + third.multiply(BigDecimal.valueOf(3)));
        System.out.println("lost      = " + ten.subtract(third.multiply(BigDecimal.valueOf(3))));
    }
}
