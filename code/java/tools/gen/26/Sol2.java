import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Sol2 {
    static Map<String, List<String>> parse(String raw) {
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

    public static void main(String[] args) {
        String[] queries = {
            null,
            "",
            "tag=work",
            "tag=a&tag=b",
            "q=",
            "flag",
            "q=hello+world&q=a%20b",
        };

        for (String query : queries) {
            System.out.printf("%-24s -> %s%n",
                    query == null ? "(no query at all)" : "'" + query + "'", render(parse(query)));
        }
        System.out.println();
        System.out.println("null and \"\" both give an empty map, and that is the first decision");
        System.out.println("'flag' has no equals sign: present, with an empty value, not absent");
        System.out.println("a repeated name keeps both values, in the order they were written");
    }

    /** Quotes every value, so an empty one is visible rather than an empty pair of brackets. */
    static String render(Map<String, List<String>> params) {
        StringBuilder out = new StringBuilder("{");
        params.forEach((name, values) -> {
            if (out.length() > 1) {
                out.append(", ");
            }
            out.append(name).append("=[");
            for (int i = 0; i < values.size(); i++) {
                out.append(i == 0 ? "" : ", ").append('\'').append(values.get(i)).append('\'');
            }
            out.append(']');
        });
        return out.append('}').toString();
    }
}
