import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Sol3 {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
            exchange.getResponseHeaders().set("Cache-Control", "no-store");
            exchange.getResponseHeaders().set("Content-Length", "999");
            byte[] body = "{\"ok\":true}".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.print(show(headOf(get(server, "/"))));
        server.stop(0);

        System.out.println();
        System.out.println("Content-Length was set to 999 and the response says 11");
        System.out.println("the argument to sendResponseHeaders is the length; a header cannot override it");
        System.out.println("the server also re-cased Content-Type to Content-type, which is legal");
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

    static String headOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(0, end + 4);
    }

    static String show(String text) {
        if (text.endsWith("\r\n")) {
            text = text.substring(0, text.length() - 2);
        }
        StringBuilder out = new StringBuilder();
        for (String line : text.split("\r\n", -1)) {
            if (line.startsWith("Date:")) {
                line = "Date: <masked>";
            }
            out.append(line.isEmpty() ? "|" : "| " + line).append('\n');
        }
        return out.toString();
    }
}
