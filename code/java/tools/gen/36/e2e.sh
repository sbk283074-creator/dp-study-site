cat > EndToEnd.java <<'JAVA'
import com.sun.net.httpserver.HttpServer;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class EndToEnd {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/healthz", exchange -> {
            byte[] body = "ok".getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().add("Content-Type", "text/plain");
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        server.createContext("/echo", exchange -> {
            byte[] body = exchange.getRequestBody().readAllBytes();
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });
        ExecutorService workers = Executors.newFixedThreadPool(4);
        server.setExecutor(workers);
        server.start();

        int port = server.getAddress().getPort();
        System.out.println("port is ephemeral  : " + (port > 0));

        HttpURLConnection health = (HttpURLConnection)
                URI.create("http://127.0.0.1:" + port + "/healthz").toURL().openConnection();
        System.out.println("healthz status     : " + health.getResponseCode());
        System.out.println("healthz body       : "
                + new String(health.getInputStream().readAllBytes(), StandardCharsets.UTF_8));

        HttpURLConnection echo = (HttpURLConnection)
                URI.create("http://127.0.0.1:" + port + "/echo").toURL().openConnection();
        echo.setRequestMethod("POST");
        echo.setDoOutput(true);
        echo.getOutputStream().write("hello".getBytes(StandardCharsets.UTF_8));
        System.out.println("echo status        : " + echo.getResponseCode());
        System.out.println("echo body          : "
                + new String(echo.getInputStream().readAllBytes(), StandardCharsets.UTF_8));

        HttpURLConnection missing = (HttpURLConnection)
                URI.create("http://127.0.0.1:" + port + "/nope").toURL().openConnection();
        System.out.println("missing status     : " + missing.getResponseCode());

        server.stop(0);
        workers.shutdownNow();
        System.out.println("workers stopped  : " + workers.isShutdown());
        System.out.println();
        System.out.println("a real socket, a real client, a real status line. Nothing here is");
        System.out.println("mocked, and the port is 0 so the kernel picks one -- which is what");
        System.out.println("makes it safe to run this on a build machine next to anything else");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out EndToEnd.java
java -cp out EndToEnd
