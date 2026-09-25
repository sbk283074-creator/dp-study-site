import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Method plus path pattern to handler, with the two failure answers kept apart. */
public final class Router {
    public interface Handler {
        Response handle(Request request);
    }

    record Route(String method, String[] pattern, Handler handler) {}

    private final List<Route> routes = new ArrayList<>();

    public Router get(String pattern, Handler handler) {
        return add("GET", pattern, handler);
    }

    public Router post(String pattern, Handler handler) {
        return add("POST", pattern, handler);
    }

    public Router delete(String pattern, Handler handler) {
        return add("DELETE", pattern, handler);
    }

    private Router add(String method, String pattern, Handler handler) {
        routes.add(new Route(method, pattern.split("/"), handler));
        return this;
    }

    public int size() {
        return routes.size();
    }

    public Response route(Request request) {
        List<String> allowed = new ArrayList<>();
        for (Route route : routes) {
            Map<String, String> vars = match(route.pattern(), request.path());
            if (vars == null) {
                continue;
            }
            if (!route.method().equals(request.method())) {
                if (!allowed.contains(route.method())) {
                    allowed.add(route.method());
                }
                continue;
            }
            return route.handler().handle(request.withVars(vars));
        }
        if (!allowed.isEmpty()) {
            return Response.methodNotAllowed(request.method(), String.join(", ", allowed));
        }
        return Response.notFound(request.path());
    }

    /** The path variables, or null when the pattern does not match. */
    static Map<String, String> match(String[] pattern, String path) {
        String[] parts = path.split("/");
        if (parts.length != pattern.length) {
            return null;
        }
        Map<String, String> vars = new LinkedHashMap<>();
        for (int i = 0; i < pattern.length; i++) {
            if (pattern[i].startsWith("{")) {
                vars.put(pattern[i].substring(1, pattern[i].length() - 1), parts[i]);
            } else if (!pattern[i].equals(parts[i])) {
                return null;
            }
        }
        return vars;
    }
}
