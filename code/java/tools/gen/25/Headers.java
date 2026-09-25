import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class Headers {
    static final String BLOCK =
            "Content-Type: text/plain; charset=utf-8\r\n"
            + "content-length: 12\r\n"
            + "Set-Cookie: a=1\r\n"
            + "Set-Cookie: b=2\r\n"
            + "Location: http://example.com/notes?page=2\r\n"
            + "X-Note:   padded   \r\n";

    public static void main(String[] args) {
        Map<String, List<String>> headers = new LinkedHashMap<>();
        for (String line : BLOCK.split("\r\n", -1)) {
            if (line.isEmpty()) {
                continue;
            }
            int colon = line.indexOf(':');
            String name = line.substring(0, colon).toLowerCase(Locale.ROOT);
            String value = line.substring(colon + 1).trim();
            headers.computeIfAbsent(name, key -> new ArrayList<>()).add(value);
        }

        for (Map.Entry<String, List<String>> entry : headers.entrySet()) {
            System.out.printf("%-15s %s%n", entry.getKey(), entry.getValue());
        }
        System.out.println();
        System.out.println("Content-Type and content-length became one key: names are case-insensitive");
        System.out.println("a name may appear twice, so a value is a list and never a String");
        System.out.println("Location's value contains a colon, so the split must be on the first one");
    }
}
