import java.util.List;
import java.util.Map;

/** Everything a handler is allowed to know about the request. No socket, no exchange. */
public record Request(String method, String path, Map<String, List<String>> query,
                      Map<String, String> headers, String body, Map<String, String> vars) {

    /** The shape a test or a demo uses, with no query, no headers and no path variables. */
    public Request(String method, String path, String body) {
        this(method, path, Map.of(), Map.of(), body, Map.of());
    }

    /** The same request, with the path variables the router pulled out of the pattern. */
    public Request withVars(Map<String, String> vars) {
        return new Request(method, path, query, headers, body, vars);
    }

    public String var(String name) {
        String value = vars.get(name);
        if (value == null) {
            throw new IllegalArgumentException("no path variable " + name + " on " + path);
        }
        return value;
    }

    public String header(String name) {
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            if (entry.getKey().equalsIgnoreCase(name)) {
                return entry.getValue();
            }
        }
        return null;
    }

    public String query(String name) {
        List<String> values = query.get(name);
        return values == null || values.isEmpty() ? null : values.get(0);
    }
}
