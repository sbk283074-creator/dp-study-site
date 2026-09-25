import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;

public class InstantsZones {
    public static void main(String[] args) {
        Instant fixed = Instant.parse("2026-03-14T12:00:00Z");
        System.out.println("instant  = " + fixed);
        System.out.println("epochSec = " + fixed.getEpochSecond());

        for (String id : new String[] {"UTC", "Europe/London", "Asia/Shanghai", "America/New_York"}) {
            ZonedDateTime z = fixed.atZone(ZoneId.of(id));
            System.out.printf("%-16s %s  offset=%s%n", id, z.toLocalDateTime(), z.getOffset());
        }
    }
}
