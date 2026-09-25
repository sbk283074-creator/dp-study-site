import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * A template is text with {@code {{name}}} placeholders.
 *
 * <p>Every substitution is escaped. {@code {{{name}}}} opts out, and opting out is the only way to
 * get an unescaped value into a page -- so a search for the raw marker finds every risk in a codebase.
 */
public final class Template {
    private record Part(String literal, String name, boolean raw) {}

    private final List<Part> parts;

    private Template(List<Part> parts) {
        this.parts = List.copyOf(parts);
    }

    public static Template of(String text) {
        List<Part> parts = new ArrayList<>();
        int at = 0;
        while (true) {
            int open = text.indexOf("{{", at);
            if (open < 0) {
                parts.add(new Part(text.substring(at), null, false));
                return new Template(parts);
            }
            parts.add(new Part(text.substring(at, open), null, false));

            boolean raw = text.startsWith("{{{", open);
            String openToken = raw ? "{{{" : "{{";
            String closeToken = raw ? "}}}" : "}}";
            int close = text.indexOf(closeToken, open + openToken.length());
            if (close < 0) {
                throw new IllegalArgumentException("unclosed placeholder at index " + open);
            }
            String name = text.substring(open + openToken.length(), close).trim();
            parts.add(new Part(null, name, raw));
            at = close + closeToken.length();
        }
    }

    public String render(Map<String, String> values) {
        StringBuilder out = new StringBuilder();
        for (Part part : parts) {
            if (part.name() == null) {
                out.append(part.literal());
            } else if (!values.containsKey(part.name())) {
                throw new IllegalArgumentException("no value for " + part.name());
            } else {
                String value = values.get(part.name());
                out.append(part.raw() ? value : Html.escape(value));
            }
        }
        return out.toString();
    }
}
