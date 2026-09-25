import java.util.Map;

public class RouteDemo {
    static Router router() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("every note"));
        router.get("/notes/{id}", request -> Response.ok("note " + request.var("id")));
        router.post("/notes", request -> Response.ok("created from '" + request.body() + "'"));
        router.delete("/notes/{id}", request -> Response.ok("deleted " + request.var("id")));
        return router;
    }

    record Call(String method, String path, String body) {}

    public static void main(String[] args) {
        Router router = router();
        System.out.println("routes: " + router.size());
        System.out.println();

        Call[] calls = {
            new Call("GET", "/notes", ""),
            new Call("GET", "/notes/7", ""),
            new Call("POST", "/notes", "milk"),
            new Call("DELETE", "/notes/7", ""),
            new Call("GET", "/notes/7/edit", ""),
            new Call("PUT", "/notes", ""),
            new Call("DELETE", "/notes", ""),
            new Call("GET", "/other", ""),
        };

        for (Call call : calls) {
            Request request = new Request(call.method(), call.path(), call.body());
            Response response = router.route(request);
            System.out.printf("%-7s %-16s -> %d  %s%n",
                    call.method(), call.path(), response.status(), response.body());
        }
        System.out.println();
        System.out.println("405 and 404 are different answers: PUT /notes found a route and rejected the method");
    }
}
