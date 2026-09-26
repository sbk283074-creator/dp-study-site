import java.util.LinkedHashMap;
import java.util.Map;

/** The Cookie and Set-Cookie headers, and the fact that they are not the same shape. */
public final class Cookies {

    private Cookies() {
    }

    /** A request's Cookie header: name=value pairs, and nothing else. */
    public static Map<String, String> parse(String header) {
        Map<String, String> out = new LinkedHashMap<>();
        if (header == null || header.isEmpty()) {
            return out;
        }
        for (String part : header.split(";")) {
            int at = part.indexOf('=');
            if (at <= 0) {
                continue;
            }
            out.put(part.substring(0, at).trim(), part.substring(at + 1).trim());
        }
        return out;
    }

    /** A response's Set-Cookie: one pair, then attributes. */
    public static String setCookie(String name, String value, String path, boolean httpOnly,
                                   boolean secure, String sameSite, long maxAgeSeconds) {
        StringBuilder out = new StringBuilder();
        out.append(name).append('=').append(value);
        if (path != null) {
            out.append("; Path=").append(path);
        }
        if (maxAgeSeconds >= 0) {
            out.append("; Max-Age=").append(maxAgeSeconds);
        }
        if (httpOnly) {
            out.append("; HttpOnly");
        }
        if (secure) {
            out.append("; Secure");
        }
        if (sameSite != null) {
            out.append("; SameSite=").append(sameSite);
        }
        return out.toString();
    }
}
