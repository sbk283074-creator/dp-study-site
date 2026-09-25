import java.math.BigDecimal;
import java.math.RoundingMode;

public class BigDecimalBasics {
    public static void main(String[] args) {
        double sum = 0.1 + 0.2;
        System.out.println("double sum   = " + sum);
        System.out.println("double == 0.3= " + (sum == 0.3));

        BigDecimal a = new BigDecimal("0.1");
        BigDecimal b = new BigDecimal("0.2");
        System.out.println("decimal sum  = " + a.add(b));
        System.out.println("decimal == .3= " + a.add(b).equals(new BigDecimal("0.3")));

        System.out.println("from double  = " + new BigDecimal(0.1));
        System.out.println("valueOf      = " + BigDecimal.valueOf(0.1));

        System.out.println("scale 0.30   = " + new BigDecimal("0.30").scale());
        System.out.println("equals 2.0   = " + new BigDecimal("2.0").equals(new BigDecimal("2.00")));
        System.out.println("compare 2.0  = " + new BigDecimal("2.0").compareTo(new BigDecimal("2.00")));
        System.out.println("stripped     = " + new BigDecimal("2.00").stripTrailingZeros());

        System.out.println("half up      = " + new BigDecimal("2.345").setScale(2, RoundingMode.HALF_UP));
        System.out.println("half even .5 = " + new BigDecimal("2.345").setScale(2, RoundingMode.HALF_EVEN));
        System.out.println("half even .6 = " + new BigDecimal("2.355").setScale(2, RoundingMode.HALF_EVEN));

        double qty = 12;
        double price = 0.35;
        System.out.println("double line  = " + (qty * price));
        System.out.println("decimal line = "
                + new BigDecimal("0.35").multiply(BigDecimal.valueOf(qty)));
    }
}
