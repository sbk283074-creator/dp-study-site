import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

public class Parsing {
    public static void main(String[] args) {
        DateTimeFormatter iso = DateTimeFormatter.ISO_LOCAL_DATE;
        DateTimeFormatter dmy = DateTimeFormatter.ofPattern("dd/MM/yyyy");

        System.out.println("iso       = " + LocalDate.parse("2026-03-14", iso));
        System.out.println("dmy       = " + LocalDate.parse("14/03/2026", dmy));
        System.out.println("roundTrip = " + LocalDate.parse("14/03/2026", dmy).format(dmy));

        try {
            LocalDate.parse("2026-13-01", iso);
        } catch (DateTimeParseException e) {
            System.out.println("rejected  = " + e.getClass().getSimpleName()
                    + " on " + e.getParsedString());
        }
    }
}
