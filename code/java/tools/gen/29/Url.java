import java.util.List;
import java.util.Locale;

/** A URL is safe in an href only if its scheme is one this service allows. */
public final class Url {
    private static final List<String> ALLOWED = List.of("http", "https", "mailto");

    private Url() {}

    /**
     * True when the text is a relative reference, or an absolute URL whose scheme is allowed.
     *
     * <p>The scheme is everything before the first colon, but only when that colon comes before any
     * slash, query or fragment -- otherwise the colon belongs to a path, as in {@code /a:b}.
     */
    public static boolean isSafe(String url) {
        String trimmed = url.strip();
        int colon = trimmed.indexOf(':');
        if (colon < 0) {
            return true;
        }
        if (comesBefore(trimmed, colon, '/') || comesBefore(trimmed, colon, '?')
                || comesBefore(trimmed, colon, '#')) {
            return true;
        }
        String scheme = trimmed.substring(0, colon).toLowerCase(Locale.ROOT);
        return ALLOWED.contains(scheme);
    }

    private static boolean comesBefore(String text, int colon, char c) {
        int at = text.indexOf(c);
        return at >= 0 && at < colon;
    }
}
