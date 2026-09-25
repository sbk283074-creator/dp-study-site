cat > Errors.java <<'EOF'
import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Errors {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);

        server.createContext("/uncaught", exchange -> {
            throw new IllegalStateException("nobody caught this");
        });
        server.createContext("/caught", exchange -> {
            Response response;
            try {
                throw new IllegalStateException("somebody caught this");
            } catch (RuntimeException e) {
                response = Response.text(500, "the service failed: " + e.getMessage());
            }
            response.writeTo(exchange);
        });
        server.start();

        for (String path : new String[] {"/uncaught", "/caught"}) {
            String response = call(server, path);
            System.out.println("GET " + path + " ->");
            if (response.isEmpty()) {
                System.out.println("  the client received nothing at all");
            } else {
                System.out.println("  " + response.split("\r\n", 2)[0]);
                System.out.println("  " + bodyOf(response));
            }
        }
        server.stop(0);

        System.out.println();
        System.out.println("an uncaught handler exception closes the connection with no response");
        System.out.println("the catch-all in the dispatcher is the only thing that can turn it into a 500");
    }

    static String call(HttpServer server, String path) throws Exception {
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

    static String bodyOf(String response) {
        int end = response.indexOf("\r\n\r\n");
        return end < 0 ? "(no body)" : response.substring(end + 4).trim();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Errors.java
java -cp out Errors
