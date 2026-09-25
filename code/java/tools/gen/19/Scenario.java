import java.math.BigDecimal;
import java.math.RoundingMode;

public class Scenario {
    static long centsFromDouble(String amount) {
        return Math.round(Double.parseDouble(amount) * 100);
    }

    static long centsExact(String amount) {
        return new BigDecimal(amount)
                .movePointRight(2)
                .setScale(0, RoundingMode.HALF_UP)
                .longValueExact();
    }

    public static void main(String[] args) {
        String[] amounts = {"19.99", "0.35", "1.005", "2.675"};
        int differences = 0;
        for (String amount : amounts) {
            long viaDouble = centsFromDouble(amount);
            long exact = centsExact(amount);
            boolean same = viaDouble == exact;
            if (!same) {
                differences++;
            }
            String note = same ? "" : "  <- differs";
            System.out.printf("%-6s double=%4d exact=%4d%s%n", amount, viaDouble, exact, note);
        }
        System.out.println("differed on " + differences + " of " + amounts.length);
    }
}
