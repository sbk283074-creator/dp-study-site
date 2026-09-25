import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Sol4 {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            exchange.getResponseHeaders().set("X-Tag", "first");
            exchange.getResponseHeaders().set("X-Tag", "second");
            exchange.getResponseHeaders().set("Set-Cookie", "a=1");
            exchange.getResponseHeaders().add("Set-Cookie", "b=2");
            byte[] body = "ok".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.start();

        System.out.print(show(headOf(get(server, "/"))));
        server.stop(0);

        System.out.println();
        System.out.println("set replaced 'first' with 'second'; add appended a second Set-Cookie");
        System.out.println("the server re-cased Set-Cookie to Set-cookie on the way out, which is legal");
        System.out.println("a response header map is a map to a list, exactly as on the way in");
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
