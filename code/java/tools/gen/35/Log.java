import java.util.ArrayList;
import java.util.List;

/**
 * One JSON object per line, with no timestamp in it. A real logger stamps every
 * line; this one numbers them, because a transcript that changes every run is a
 * transcript that cannot be checked.
 */
public final class Log {

    private static final List<String> SECRETS = List.of("password", "token", "secret");

    private final List<String> lines = new ArrayList<>();
    private final String threshold;
    private static final List<String> ORDER = List.of("debug", "info", "warn", "error");

    public Log(String threshold) {
        this.threshold = threshold;
    }

    public boolean enabled(String level) {
        return ORDER.indexOf(level) >= ORDER.indexOf(threshold);
    }

    public void line(String level, String message, String... fields) {
        if (!enabled(level)) {
            return;
        }
        StringBuilder out = new StringBuilder();
        out.append("{\"seq\": ").append(lines.size() + 1);
        out.append(", \"level\": \"").append(level).append('"');
        out.append(", \"msg\": \"").append(escape(message)).append('"');
        for (int i = 0; i + 1 < fields.length; i += 2) {
            String value = SECRETS.contains(fields[i]) ? "<redacted>" : fields[i + 1];
            out.append(", \"").append(escape(fields[i])).append("\": \"")
                    .append(escape(value)).append('"');
        }
        out.append('}');
        String built = out.toString();
        lines.add(built);
        System.out.println(built);
    }

    /** A newline in a value is a fake log line, so it becomes two characters. */
    public static String escape(String value) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            switch (c) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                default -> {
                    if (c < 0x20) {
                        out.append(String.format("\\u%04x", (int) c));
                    } else {
                        out.append(c);
                    }
                }
            }
        }
        return out.toString();
    }

    public int written() {
        return lines.size();
    }
}
