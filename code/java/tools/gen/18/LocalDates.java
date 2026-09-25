import java.time.LocalDate;
import java.time.Month;
import java.time.Period;
import java.time.temporal.ChronoUnit;

public class LocalDates {
    public static void main(String[] args) {
        LocalDate d = LocalDate.of(2026, Month.MARCH, 14);

        System.out.println("date       = " + d);
        System.out.println("dayOfWeek  = " + d.getDayOfWeek());
        System.out.println("dayOfYear  = " + d.getDayOfYear());
        System.out.println("plusDays   = " + d.plusDays(10));
        System.out.println("minusMonths= " + d.minusMonths(3));
        System.out.println("isLeapYear = " + d.isLeapYear());

        LocalDate e = LocalDate.of(2026, 6, 1);
        System.out.println("period     = " + Period.between(d, e));
        System.out.println("days apart = " + ChronoUnit.DAYS.between(d, e));
        System.out.println("months     = " + ChronoUnit.MONTHS.between(d, e));
        System.out.println("equals     = " + d.equals(LocalDate.of(2026, 3, 14)));
        System.out.println("compareTo  = " + Integer.signum(d.compareTo(e)));
    }
}
