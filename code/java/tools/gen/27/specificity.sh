cat > Specificity.java <<'EOF'
import java.util.List;

public class Specificity {
    static Router idFirst() {
        Router router = new Router();
        router.get("/notes/{id}", request -> Response.ok("a note with id=" + request.var("id")));
        router.get("/notes/latest", request -> Response.ok("the latest note"));
        return router;
    }

    static Router literalFirst() {
        Router router = new Router();
        router.get("/notes/latest", request -> Response.ok("the latest note"));
        router.get("/notes/{id}", request -> Response.ok("a note with id=" + request.var("id")));
        return router;
    }

    public static void main(String[] args) {
        List<Router> routers = List.of(idFirst(), literalFirst());
        String[] labels = {"{id} registered first", "literal registered first"};

        for (int i = 0; i < routers.size(); i++) {
            System.out.println(labels[i] + ":");
            for (String path : List.of("/notes/7", "/notes/latest")) {
                Request request = new Request("GET", path, "");
                Response response = routers.get(i).route(request);
                System.out.printf("  %-16s -> %d  %s%n", path, response.status(), response.body());
            }
        }

        System.out.println();
        System.out.println("both patterns match /notes/latest, and the first one registered wins");
        System.out.println("so a literal path has to be registered before the variable that would swallow it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Specificity.java
java -cp out Specificity
