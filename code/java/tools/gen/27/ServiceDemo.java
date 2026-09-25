import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class ServiceDemo {
    static List<String> notes = new ArrayList<>(List.of("groceries", "reading"));

    static Router routes() {
        Router router = new Router();
        router.get("/notes", request -> Response.ok(String.join(", ", notes)));
        router.get("/notes/{id}", request -> {
            int id = Integer.parseInt(request.var("id"));
            return Response.ok(notes.get(id));
        });
        router.post("/notes", request -> {
            notes.add(request.body());
            return Response.text(201, "added " + request.body());
        });
        router.get("/boom", request -> {
            throw new IllegalStateException("the note store is on fire");
        });
        return router;
    }

    public static void main(String[] args) throws Exception {
        Router router = routes();
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            Response response;
            try {
                response = router.route(Requests.from(exchange));
            } catch (RuntimeException e) {
                response = Response.text(500, "the service failed: " + e.getMessage());
            }
            response.writeTo(exchange);
        });
        server.start();

        String[][] calls = {
            {"GET", "/notes", null},
            {"GET", "/notes/1", null},
            {"POST", "/notes", "buy milk"},
            {"GET", "/notes", null},
            {"PUT", "/notes", null},
            {"GET", "/nowhere", null},
            {"GET", "/boom", null},
        };

        for (String[] call : calls) {
            String response = call(server, call[0], call[1], call[2]);
            System.out.printf("%-6s %-12s -> %s%n", call[0], call[1], statusLine(response));
            System.out.println("        " + bodyOf(response));
        }
        server.stop(0);

        System.out.println();
        System.out.println("one handler threw and the client still got a complete 500 response");
    }

    static String call(HttpServer server, String method, String path, String body) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            StringBuilder request = new StringBuilder(method).append(' ').append(path)
                    .append(" HTTP/1.1\r\nHost: localhost\r\n");
            if (body != null) {
                request.append("Content-Length: ")
                        .append(body.getBytes(StandardCharsets.UTF_8).length).append("\r\n");
            }
            request.append("Connection: close\r\n\r\n");
            if (body != null) {
                request.append(body);
            }
            OutputStream out = socket.getOutputStream();
            out.write(request.toString().getBytes(StandardCharsets.UTF_8));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
            return bytes.toString(StandardCharsets.UTF_8);
        }
    }

    static String statusLine(String response) {
        return response.split("\r\n", 2)[0];
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "" : response.substring(end + 4).trim();
    }
}
