import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class Contexts {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/notes", exchange -> {
            byte[] body = ("the /notes handler saw "
                    + exchange.getRequestURI().getPath()).getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.createContext("/", exchange -> {
            byte[] body = "the / handler".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        for (String path : List.of("/notes", "/notes/7", "/notes/7/edit", "/noteworthy", "/other")) {
            String response = get(server, path);
            System.out.printf("%-16s %-24s %s%n", path, statusLine(response), bodyOf(response));
        }
        server.stop(0);

        System.out.println();
        System.out.println("/noteworthy is not /notes: a match stops at a path boundary");
        System.out.println("and where two contexts both match, the longest one wins");
    }

    static String get(HttpServer server, String path) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(("GET " + path + " HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
                    .getBytes(StandardCharsets.US_ASCII));
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
