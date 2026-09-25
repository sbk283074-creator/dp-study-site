import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.temporal.ChronoUnit;

public class LocalTimes {
    public static void main(String[] args) {
        LocalTime start = LocalTime.of(9, 15);
        LocalTime end = LocalTime.of(17, 45);
        Duration shift = Duration.between(start, end);

        System.out.println("duration   = " + shift);
        System.out.println("minutes    = " + shift.toMinutes());
        System.out.println("parts      = " + shift.toHoursPart() + "h " + shift.toMinutesPart() + "m");
        System.out.println("plus       = " + start.plus(shift));

        Duration overnight = Duration.between(LocalTime.of(23, 0), LocalTime.of(1, 30));
        System.out.println("overnight  = " + overnight);

        LocalDateTime dt = LocalDateTime.of(2026, 3, 14, 9, 15, 30);
        System.out.println("datetime   = " + dt);
        System.out.println("truncated  = " + dt.truncatedTo(ChronoUnit.HOURS));
    }
}
