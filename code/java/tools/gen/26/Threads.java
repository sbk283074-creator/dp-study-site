import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Threads {
    public static void main(String[] args) throws Exception {
        System.out.println("no executor set:");
        System.out.println("  " + measure(false));
        System.out.println();
        System.out.println("a fixed pool of two:");
        System.out.println("  " + measure(true));
        System.out.println();
        System.out.println("the default executor is one thread, and the documentation leaves that to you");
    }

    /** Fires two requests at once and reports what the handlers actually observed. */
    static String measure(boolean pooled) throws Exception {
        Set<String> threads = ConcurrentHashMap.newKeySet();
        CountDownLatch bothArrived = new CountDownLatch(2);
        int[] sawBoth = {0};

        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            threads.add(Thread.currentThread().getName());
            bothArrived.countDown();
            try {
                if (bothArrived.await(3, TimeUnit.SECONDS)) {
                    sawBoth[0]++;
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            byte[] body = "ok".getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream out = exchange.getResponseBody()) {
                out.write(body);
            }
        });

        ExecutorService pool = null;
        if (pooled) {
            pool = Executors.newFixedThreadPool(2);
            server.setExecutor(pool);
        }
        server.start();

        Thread first = new Thread(() -> quietlyGet(server));
        Thread second = new Thread(() -> quietlyGet(server));
        first.start();
        second.start();
        first.join();
        second.join();
        server.stop(0);
        if (pool != null) {
            pool.shutdown();
        }

        return threads.size() + " thread(s) answered; handler(s) that saw both requests in flight: "
                + sawBoth[0];
    }

    static void quietlyGet(HttpServer server) {
        try (Socket socket = new Socket("127.0.0.1", server.getAddress().getPort())) {
            OutputStream out = socket.getOutputStream();
            out.write("GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                    .getBytes(StandardCharsets.US_ASCII));
            out.flush();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(bytes);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
