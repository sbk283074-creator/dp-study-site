import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class Introspect {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/notes", exchange -> {
            String body = new String(exchange.getRequestBody().readAllBytes(),
                    StandardCharsets.UTF_8);
            String report = line("method", exchange.getRequestMethod())
                    + line("path", exchange.getRequestURI().getPath())
                    + line("rawQuery", String.valueOf(exchange.getRequestURI().getRawQuery()))
                    + line("Host", header(exchange, "Host"))
                    + line("Content-Type", header(exchange, "Content-Type"))
                    + line("X-Note", header(exchange, "x-note"))
                    + line("body", "'" + body + "' (" + body.length() + " character(s))");
            byte[] bytes = report.getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(bytes);
            }
        });
        server.start();

        System.out.print(bodyOf(post(server)));
        server.stop(0);

        System.out.println();
        System.out.println("the handler was handed a parsed request: no framing, no socket, no CRLF");
        System.out.println("header lookup ignores case, so 'x-note' found 'X-Note'");
    }

    static String line(String label, String value) {
        return String.format("%-13s%s%n", label, value);
    }

    static String header(com.sun.net.httpserver.HttpExchange exchange, String name) {
        List<String> values = exchange.getRequestHeaders().get(name);
        return values == null ? "(absent)" : String.join(", ", values);
    }

    static String post(HttpServer server) throws Exception {
        String body = "remember the milk";
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(("POST /notes?tag=work HTTP/1.1\r\n"
                    + "Host: localhost\r\n"
                    + "Content-Type: text/plain; charset=utf-8\r\n"
                    + "X-Note: kept\r\n"
                    + "Content-Length: " + body.length() + "\r\n"
                    + "Connection: close\r\n"
                    + "\r\n"
                    + body).getBytes(StandardCharsets.US_ASCII));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
            return bytes.toString(StandardCharsets.UTF_8);
        }
    }

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(end + 4);
    }
}
