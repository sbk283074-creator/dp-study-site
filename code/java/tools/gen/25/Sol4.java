import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class Sol4 {
    static final List<String> REQUESTS = List.of(
            "GET /one HTTP/1.1\r\nHost: localhost\r\n\r\n",
            "GET /two HTTP/1.1\r\nHost: localhost\r\n\r\n");

    public static void main(String[] args) throws Exception {
        List<String> seen = new ArrayList<>();

        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    InputStream in = socket.getInputStream();
                    OutputStream out = socket.getOutputStream();
                    for (int i = 0; i < REQUESTS.size(); i++) {
                        seen.add(readHead(in).split("\r\n")[0]);
                        String body = "reply " + (i + 1);
                        out.write(("HTTP/1.1 200 OK\r\n"
                                + "Content-Length: " + body.length() + "\r\n"
                                + "Connection: keep-alive\r\n"
                                + "\r\n"
                                + body).getBytes(StandardCharsets.US_ASCII));
                        out.flush();
                    }
                } catch (IOException e) {
                    throw new java.io.UncheckedIOException(e);
                }
            });
            server.start();

            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();
                for (String request : REQUESTS) {
                    out.write(request.getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                    String head = readHead(in);
                    int length = Integer.parseInt(head.lines()
                            .filter(l -> l.toLowerCase().startsWith("content-length:"))
                            .findFirst().orElseThrow().split(":")[1].trim());
                    in.readNBytes(length);
                }
            }
            server.join();

            System.out.println("the server handled " + seen.size()
                    + " request(s) on one connection:");
            for (String line : seen) {
                System.out.println("  " + line);
            }
            System.out.println();
            System.out.println("one socket, two request/response pairs. That is keep-alive, and it is");
            System.out.println("the reason a client must know where each body ends.");
        }
    }

    static String readHead(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        int state = 0;
        int b;
        while (state != 4 && (b = in.read()) != -1) {
            bytes.write(b);
            state = switch (state) {
                case 0 -> b == '\r' ? 1 : 0;
                case 1 -> b == '\n' ? 2 : (b == '\r' ? 1 : 0);
                case 2 -> b == '\r' ? 3 : 0;
                default -> b == '\n' ? 4 : 0;
            };
        }
        return bytes.toString(StandardCharsets.US_ASCII);
    }
}
