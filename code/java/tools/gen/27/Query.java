import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Query {
    private Query() {}

    /** A name with no `=` is present with an empty value; a repeated name keeps every value. */
    public static Map<String, List<String>> parse(String raw) {
        Map<String, List<String>> params = new LinkedHashMap<>();
        if (raw == null || raw.isEmpty()) {
            return params;
        }
        for (String pair : raw.split("&")) {
            int equals = pair.indexOf('=');
            String name = equals < 0 ? pair : pair.substring(0, equals);
            String value = equals < 0
                    ? ""
                    : URLDecoder.decode(pair.substring(equals + 1), StandardCharsets.UTF_8);
            params.computeIfAbsent(name, key -> new ArrayList<>()).add(value);
        }
        return params;
    }
}
