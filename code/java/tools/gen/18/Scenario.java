import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;

public class Scenario {
    record Line(String sku, int qty, BigDecimal unitPrice) {}

    static final BigDecimal TAX = new BigDecimal("0.20");

    public static void main(String[] args) {
        List<Line> lines = List.of(
                new Line("A-1", 3, new BigDecimal("19.99")),
                new Line("B-7", 1, new BigDecimal("4.05")),
                new Line("C-3", 12, new BigDecimal("0.35")));

        BigDecimal net = BigDecimal.ZERO;
        for (Line l : lines) {
            BigDecimal lineTotal = l.unitPrice().multiply(BigDecimal.valueOf(l.qty()));
            net = net.add(lineTotal);
            System.out.printf("%-4s %3d x %6s = %8s%n", l.sku(), l.qty(), l.unitPrice(), lineTotal);
        }

        BigDecimal tax = net.multiply(TAX).setScale(2, RoundingMode.HALF_UP);
        BigDecimal gross = net.add(tax);

        System.out.println("net    = " + net);
        System.out.println("tax    = " + tax);
        System.out.println("gross  = " + gross);

        LocalDate issued = LocalDate.of(2026, 3, 14);
        LocalDate due = issued.plusDays(30);
        System.out.println("issued = " + issued);
        System.out.println("due    = " + due);
        System.out.println("terms  = " + ChronoUnit.DAYS.between(issued, due) + " days");
    }
}
