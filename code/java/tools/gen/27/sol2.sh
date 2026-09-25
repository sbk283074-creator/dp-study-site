cat > Sol2.java <<'EOF'
import java.util.List;

public class Sol2 {
    static Router routes() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("every note"));
        router.get("/notes/{id}", request -> {
            String raw = request.var("id");
            try {
                return Response.ok("note " + Integer.parseInt(raw));
            } catch (NumberFormatException e) {
                return Response.text(400, "'" + raw + "' is not an id");
            }
        });
        return router;
    }

    public static void main(String[] args) {
        Router router = routes();
        for (String path : List.of("/notes", "/notes/7", "/notes/seven", "/notes/7/edit", "/other")) {
            Response response = router.route(new Request("GET", path, ""));
            System.out.printf("%-16s -> %d  %s%n", path, response.status(), response.body());
        }
        System.out.println();
        System.out.println("three different answers: 200 found it, 400 the id is malformed, 404 no such route");
        System.out.println("a route that exists and an id that is wrong are not the same failure");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
