import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.time.temporal.ChronoUnit;

public class Sol4 {
    public static void main(String[] args) {
        LocalDate from = LocalDate.of(2025, 1, 31);
        LocalDate to = LocalDate.of(2025, 3, 1);

        System.out.println("period     = " + Period.between(from, to));
        System.out.println("periodDays = " + Period.between(from, to).getDays());
        System.out.println("exactDays  = " + ChronoUnit.DAYS.between(from, to));

        LocalDateTime a = LocalDateTime.of(2025, 3, 8, 12, 0);
        LocalDateTime b = a.plusDays(1);
        System.out.println("duration   = " + Duration.between(a, b));
        System.out.println("plusPeriod = " + a.plus(Period.ofDays(1)));
        System.out.println("normalised = " + from.plus(Period.between(from, to)));
        System.out.println("roundTrip  = " + from.plus(Period.between(from, to)).equals(to));
    }
}
