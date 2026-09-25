import java.util.Map;

/** Writes a Json value back out, escaping what JSON requires. */
public final class JsonWriter {
    private JsonWriter() {}

    public static String write(Json value) {
        StringBuilder out = new StringBuilder();
        write(value, out);
        return out.toString();
    }

    /** A compact form, with no whitespace. An indenting writer is a separate decision. */
    private static void write(Json value, StringBuilder out) {
        switch (value) {
            case Json.Nil nil -> out.append("null");
            case Json.Bool b -> out.append(b.value());
            case Json.Num n -> out.append(n.raw());
            case Json.Str s -> quote(s.value(), out);
            case Json.Arr a -> {
                out.append('[');
                for (int i = 0; i < a.items().size(); i++) {
                    if (i > 0) {
                        out.append(',');
                    }
                    write(a.items().get(i), out);
                }
                out.append(']');
            }
            case Json.Obj o -> {
                out.append('{');
                boolean first = true;
                for (Map.Entry<String, Json> member : o.members().entrySet()) {
                    if (!first) {
                        out.append(',');
                    }
                    first = false;
                    quote(member.getKey(), out);
                    out.append(':');
                    write(member.getValue(), out);
                }
                out.append('}');
            }
        }
    }

    /**
     * Escape what JSON requires, and two characters it does not.
     *
     * <p>Required: the quote, the backslash, and every character below 0x20. Everything else may be
     * written raw. {@code U+2028} and {@code U+2029} are legal raw in JSON and terminate a line in
     * JavaScript, which is why a writer that emits JSON for a browser escapes them anyway.
     */
    private static void quote(String text, StringBuilder out) {
        out.append('"');
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            switch (c) {
                case '"' -> out.append("\\\"");
                case '\\' -> out.append("\\\\");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                case '\t' -> out.append("\\t");
                case '\b' -> out.append("\\b");
                case '\f' -> out.append("\\f");
                case '\u2028' -> out.append("\\u2028");
                case '\u2029' -> out.append("\\u2029");
                default -> {
                    if (c < 0x20) {
                        out.append("\\u").append(hex4(c));
                    } else {
                        out.append(c);
                    }
                }
            }
        }
        out.append('"');
    }

    /** Lower-case hex, padded to four digits, with no locale in sight. */
    private static String hex4(char c) {
        String hex = Integer.toHexString(c);
        return "0000".substring(hex.length()) + hex;
    }
}
