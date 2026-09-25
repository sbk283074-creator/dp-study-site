import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

public class Sol2 {
    static long daysUntil(LocalDate from, LocalDate deadline) {
        return ChronoUnit.DAYS.between(from, deadline);
    }

    static String status(LocalDate from, LocalDate deadline) {
        long days = daysUntil(from, deadline);
        if (days < 0) {
            return "overdue by " + (-days);
        }
        return days == 0 ? "due today" : "due in " + days;
    }

    public static void main(String[] args) {
        LocalDate issued = LocalDate.of(2026, 3, 14);
        LocalDate[] dates = {
            LocalDate.of(2026, 3, 10),
            LocalDate.of(2026, 3, 14),
            LocalDate.of(2026, 3, 20),
        };
        for (LocalDate d : dates) {
            System.out.printf("%s  %s%n", d, status(issued, d));
        }
        System.out.println("acrossFeb = " + daysUntil(LocalDate.of(2026, 1, 31),
                LocalDate.of(2026, 2, 28)));
    }
}
