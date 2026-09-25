import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/** What the adapter saw, printed from inside the handler. */
public class AdapterDemo {
    public static void main(String[] args) throws Exception {
        List<String> seen = new ArrayList<>();
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/", exchange -> {
            Request request = Requests.from(exchange);
            seen.add("method  " + request.method());
            seen.add("path    " + request.path());
            seen.add("q       " + request.query("q"));
            seen.add("tag     " + request.query("tag") + "  (the record keeps "
                    + request.query().get("tag") + ")");
            seen.add("accept  " + request.header("Accept"));
            seen.add("body    " + request.body());
            Response.ok("ok").writeTo(exchange);
        });
        server.start();

        String raw = "POST /notes?q=hot%20milk&tag=a&tag=b HTTP/1.1\r\n"
                + "Host: localhost\r\n"
                + "Accept: application/json\r\n"
                + "Content-Length: 8\r\n"
                + "Connection: close\r\n"
                + "\r\n"
                + "buy milk";
        call(server, raw);
        server.stop(0);

        for (String line : seen) {
            System.out.println(line);
        }
        System.out.println();
        System.out.println("one file read the exchange; everything above is a plain value");
    }

    static void call(HttpServer server, String raw) throws Exception {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write(raw.getBytes(StandardCharsets.UTF_8));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
        }
    }
}
