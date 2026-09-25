cat > Sol4.java <<'EOF'
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Sol4 {
    record Route(String method, String[] pattern) {}

    static final List<Route> ROUTES = List.of(
            new Route("GET", "/notes".split("/")),
            new Route("POST", "/notes".split("/")),
            new Route("GET", "/notes/{id}".split("/")),
            new Route("DELETE", "/notes/{id}".split("/")));

    /** Every method that would be accepted at this path, in registration order. */
    static List<String> methodsFor(String path) {
        Map<String, Boolean> seen = new LinkedHashMap<>();
        for (Route route : ROUTES) {
            if (Router.match(route.pattern(), path) != null) {
                seen.putIfAbsent(route.method(), Boolean.TRUE);
            }
        }
        return new ArrayList<>(seen.keySet());
    }

    public static void main(String[] args) {
        for (String path : new String[] {"/notes", "/notes/7", "/other"}) {
            List<String> methods = methodsFor(path);
            System.out.printf("%-12s -> %s%n", path,
                    methods.isEmpty() ? "(no methods; a 404)" : String.join(", ", methods));
        }
        System.out.println();
        System.out.println("this is what an Allow header is made of, and what OPTIONS would answer");
        System.out.println("it comes from the same table the router already has, so it cannot go stale");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
