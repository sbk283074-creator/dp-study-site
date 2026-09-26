import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Four layers, last one wins, and every value remembers where it came from.
 * That provenance is what makes `--print-config` an answer instead of a guess.
 */
public final class Config {

    private static final List<String> SECRETS = List.of("secret", "password", "token");

    private final Map<String, String> values = new TreeMap<>();
    private final Map<String, String> origin = new TreeMap<>();

    public void layer(Map<String, String> entries, String source) {
        for (Map.Entry<String, String> entry : entries.entrySet()) {
            values.put(entry.getKey(), entry.getValue());
            origin.put(entry.getKey(), source);
        }
    }

    public void arguments(String[] args) {
        for (String arg : args) {
            if (!arg.startsWith("--")) {
                continue;
            }
            String body = arg.substring(2);
            int at = body.indexOf('=');
            if (at <= 0) {
                continue;
            }
            values.put(body.substring(0, at), body.substring(at + 1));
            origin.put(body.substring(0, at), "arguments");
        }
    }

    public String get(String key) {
        return values.get(key);
    }

    public String originOf(String key) {
        return origin.getOrDefault(key, "missing");
    }

    public int intOf(String key, int fallback) {
        String raw = values.get(key);
        if (raw == null) {
            return fallback;
        }
        try {
            return Integer.parseInt(raw.trim());
        } catch (NumberFormatException e) {
            return Integer.MIN_VALUE;
        }
    }

    /** Every problem found at startup, so the process can die before it serves. */
    public List<String> validate() {
        List<String> problems = new ArrayList<>();
        int port = intOf("port", -1);
        if (port < 1 || port > 65535) {
            problems.add("port must be between 1 and 65535, got " + port);
        }
        String level = get("level");
        if (level == null) {
            problems.add("level is required");
        } else if (!List.of("debug", "info", "warn", "error").contains(level)) {
            problems.add("level must be one of debug, info, warn, error; got " + level);
        }
        if (get("db") == null || get("db").isEmpty()) {
            problems.add("db is required");
        }
        return problems;
    }

    /** Secrets never leave this method in the clear. */
    public String printed() {
        StringBuilder out = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : values.entrySet()) {
            if (!first) {
                out.append(", ");
            }
            first = false;
            out.append('"').append(entry.getKey()).append("\": \"");
            out.append(SECRETS.contains(entry.getKey()) ? "<redacted>" : entry.getValue());
            out.append('"');
        }
        return out.append('}').toString();
    }
}
