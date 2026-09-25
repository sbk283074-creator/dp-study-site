import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

public class Sol3 {
    static final DateTimeFormatter WIRE =
            DateTimeFormatter.ofPattern("yyyy-MM-dd", Locale.ROOT);
    static final DateTimeFormatter HUMAN =
            DateTimeFormatter.ofPattern("d MMMM yyyy", Locale.US);

    public static void main(String[] args) {
        LocalDate d = LocalDate.of(2026, 3, 14);

        System.out.println("wire      = " + d.format(WIRE));
        System.out.println("human     = " + d.format(HUMAN));
        System.out.println("parsed    = " + LocalDate.parse("2026-03-14", WIRE));
        System.out.println("roundTrip = " + LocalDate.parse(d.format(WIRE), WIRE).equals(d));
        System.out.println("german    = "
                + d.format(DateTimeFormatter.ofPattern("d MMMM yyyy", Locale.GERMAN)));
    }
}
