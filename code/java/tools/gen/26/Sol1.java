public class Sol1 {
    record Response(int status, String contentType, String body) {
        static Response text(String body) {
            return new Response(200, "text/plain; charset=utf-8", body);
        }

        static Response notFound(String path) {
            return new Response(404, "text/plain; charset=utf-8", "no such path: " + path);
        }
    }

    static Response route(String method, String path) {
        if (!method.equals("GET")) {
            return new Response(405, "text/plain; charset=utf-8", method + " is not allowed here");
        }
        if (path.startsWith("/notes/")) {
            return Response.text("note " + path.substring("/notes/".length()));
        }
        return switch (path) {
            case "/" -> Response.text("bulletin");
            case "/health" -> Response.text("ok");
            default -> Response.notFound(path);
        };
    }

    public static void main(String[] args) {
        String[][] requests = {
            {"GET", "/"},
            {"GET", "/health"},
            {"GET", "/notes/7"},
            {"POST", "/notes/7"},
            {"GET", "/other"},
        };

        for (String[] request : requests) {
            Response response = route(request[0], request[1]);
            System.out.printf("%-6s %-12s -> %d  %s%n",
                    request[0], request[1], response.status(), response.body());
        }
        System.out.println();
        System.out.println("route is a pure function of (method, path): no socket, no server, no port");
        System.out.println("that is what makes the routing table testable on its own");
    }
}
