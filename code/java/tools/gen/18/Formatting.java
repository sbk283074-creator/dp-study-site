import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

public class Formatting {
    public static void main(String[] args) {
        LocalDateTime dt = LocalDateTime.of(2026, 3, 14, 9, 5, 7);

        System.out.println("toString  = " + dt);
        System.out.println("pattern   = "
                + dt.format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")));
        System.out.println("dayNameUS = "
                + dt.format(DateTimeFormatter.ofPattern("EEEE", Locale.US)));
        System.out.println("dayNameDE = "
                + dt.format(DateTimeFormatter.ofPattern("EEEE", Locale.GERMAN)));
        System.out.println("quoted    = "
                + dt.format(DateTimeFormatter.ofPattern("'on' dd 'of' MMMM", Locale.US)));
        System.out.println("isoWeek   = " + dt.format(DateTimeFormatter.ISO_WEEK_DATE));
        System.out.println("quarter   = "
                + dt.format(DateTimeFormatter.ofPattern("QQQ", Locale.US)));
        System.out.println("unpadded  = " + dt.format(DateTimeFormatter.ofPattern("d/M/yyyy")));
    }
}
