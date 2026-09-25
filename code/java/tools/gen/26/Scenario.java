import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Scenario {
    static final String BODY = "only fourteen!";
    static volatile String failure = "(the handler did not fail)";

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/short", exchange -> {
            exchange.sendResponseHeaders(200, 100);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(BODY.getBytes(StandardCharsets.UTF_8));
            } catch (IOException e) {
                failure = e.getClass().getName() + ": " + e.getMessage();
                throw e;
            }
        });
        server.createContext("/report", exchange -> {
            byte[] body = failure.getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.println("the handler declared 100 byte(s) and wrote " + BODY.length());
        System.out.println();
        String response = get(server, "/short");
        System.out.println("what the client received:");
        System.out.print(show(headOf(response)));
        System.out.println("  ...then " + bodyLength(response) + " byte(s) of body, with 100 promised");
        System.out.println();
        System.out.println("what the handler caught:");
        System.out.println("  " + bodyOf(get(server, "/report")));
        server.stop(0);
    }

    static int bodyLength(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? 0 : response.length() - (end + 4);
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

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "" : response.substring(end + 4).trim();
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
