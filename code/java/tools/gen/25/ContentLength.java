import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;

public class ContentLength {
    static final String BODY = "hello, world";

    static final String HEAD =
            "HTTP/1.1 200 OK\r\n"
            + "Content-Type: text/plain; charset=utf-8\r\n"
            + "Content-Length: " + BODY.length() + "\r\n"
            + "\r\n";

    public static void main(String[] args) throws Exception {
        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    readHead(socket.getInputStream());
                    OutputStream out = socket.getOutputStream();
                    out.write((HEAD + BODY).getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                    Thread.sleep(1200);
                } catch (IOException | InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
            server.start();

            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();
                out.write("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
                        .getBytes(StandardCharsets.US_ASCII));
                out.flush();

                String head = readHead(in);
                int declared = Integer.parseInt(
                        head.lines().filter(l -> l.toLowerCase().startsWith("content-length:"))
                                .findFirst().orElseThrow().split(":")[1].trim());

                byte[] body = in.readNBytes(declared);
                System.out.println("Content-Length says " + declared + " byte(s)");
                System.out.println("readNBytes(" + declared + ") returned " + body.length
                        + " byte(s): " + new String(body, StandardCharsets.US_ASCII));

                socket.setSoTimeout(300);
                try {
                    int extra = in.read();
                    System.out.println("one more read returned " + extra);
                } catch (SocketTimeoutException e) {
                    System.out.println("one more read blocked for 300 ms: SocketTimeoutException");
                }
            }
            server.join();
            System.out.println();
            System.out.println("the connection was still open: Content-Length ends the body, not the close");
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
