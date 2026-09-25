import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.List;

public class Lengths {
    static final String BODY = "hello, world";

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/exact", exchange -> {
            exchange.sendResponseHeaders(200, BODY.length());
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(BODY.getBytes(StandardCharsets.UTF_8));
            }
        });
        server.createContext("/unknown", exchange -> {
            exchange.sendResponseHeaders(200, 0);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(BODY.getBytes(StandardCharsets.UTF_8));
            }
        });
        server.createContext("/none", exchange -> {
            exchange.sendResponseHeaders(204, -1);
            exchange.close();
        });
        server.start();

        for (String path : List.of("/exact", "/unknown", "/none")) {
            System.out.println(path + " ->");
            System.out.print(show(headOf(get(server, path))));
            System.out.println();
        }
        server.stop(0);

        System.out.println("12 is the body, 0 asked for chunked, -1 said there is no body at all");
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

    /** Everything up to and including the blank line that ends the head. */
    static String headOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? response : response.substring(0, end + 4);
    }

    /** Renders CRLF visibly, and masks the clock the server adds. */
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
