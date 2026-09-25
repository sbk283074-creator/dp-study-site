cat > Scenario.java <<'EOF'
import java.util.List;

public class Scenario {
    record Pair(String method, String pattern) {}

    static final List<Pair> PAIRS = List.of(
            new Pair("GET", "/notes"),
            new Pair("POST", "/notes"),
            new Pair("DELETE", "/notes/{id}"));

    /** The version that looks for the pair (method, path) and gives up when it is not there. */
    static Response naiveRoute(String method, String path) {
        for (Pair pair : PAIRS) {
            if (pair.method().equals(method)
                    && Router.match(pair.pattern().split("/"), path) != null) {
                return Response.ok("handled");
            }
        }
        return Response.notFound(path);
    }

    static Router realRouter() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("handled"));
        router.post("/notes", request -> Response.ok("handled"));
        router.delete("/notes/{id}", request -> Response.ok("handled"));
        return router;
    }

    public static void main(String[] args) {
        Router router = realRouter();

        for (String method : List.of("GET", "DELETE")) {
            String path = "/notes";
            Response naive = naiveRoute(method, path);
            Response real = router.route(new Request(method, path, ""));
            System.out.printf("%-7s %-10s naive -> %d  %s%n", method, path, naive.status(), naive.body());
            System.out.printf("%-7s %-10s real  -> %d  %s%n", method, path, real.status(), real.body());
        }

        System.out.println();
        System.out.println("the naive router collapsed two different failures into one answer");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
