/** Escaping for HTML text nodes and quoted attribute values. */
public final class Html {
    private Html() {}

    /**
     * Escapes the five characters that can change the structure of a document.
     *
     * <p>One pass, so one input character is examined once and double-escaping is impossible by
     * construction: the ampersands this method writes are never re-read.
     */
    public static String escape(String text) {
        StringBuilder out = new StringBuilder(text.length());
        for (int i = 0; i < text.length(); i++) {
            appendEscaped(out, text.charAt(i));
        }
        return out.toString();
    }

    /** Escapes only the characters named. Used to show which context needs which set. */
    public static String escapeOnly(String text, String characters) {
        StringBuilder out = new StringBuilder(text.length());
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (characters.indexOf(c) < 0) {
                out.append(c);
            } else {
                appendEscaped(out, c);
            }
        }
        return out.toString();
    }

    private static void appendEscaped(StringBuilder out, char c) {
        switch (c) {
            case '&' -> out.append("&amp;");
            case '<' -> out.append("&lt;");
            case '>' -> out.append("&gt;");
            case '"' -> out.append("&quot;");
            case '\'' -> out.append("&#39;");
            default -> out.append(c);
        }
    }
}
