import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;

public class Scenario {
    static final String BODY = "hello, world!";
    static final String REQUEST = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n";

    public static void main(String[] args) throws Exception {
        System.out.println("the body on the wire is " + BODY.length() + " byte(s): '" + BODY + "'");
        System.out.println();

        System.out.println("-- the header understates the body --");
        exchange(BODY.length() - 1);
        System.out.println();

        System.out.println("-- the header overstates the body --");
        exchange(BODY.length() + 1);
    }

    /** Serves BODY with a Content-Length of `declared` and reports what the client saw. */
    static void exchange(int declared) throws Exception {
        String head = "HTTP/1.1 200 OK\r\nContent-Length: " + declared + "\r\n\r\n";

        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    readHead(socket.getInputStream());
                    OutputStream out = socket.getOutputStream();
                    out.write((head + BODY).getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                    Thread.sleep(800);
                } catch (IOException | InterruptedException e) {
                    throw new RuntimeException(e);
                }
            });
            server.start();

            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();
                out.write(REQUEST.getBytes(StandardCharsets.US_ASCII));
                out.flush();
                readHead(in);

                System.out.println("declared " + declared + ", written " + BODY.length());
                socket.setSoTimeout(400);
                try {
                    byte[] body = in.readNBytes(declared);
                    String text = new String(body, StandardCharsets.US_ASCII);
                    System.out.println("  the client read " + body.length + " byte(s): '" + text + "'");
                    if (body.length < BODY.length()) {
                        System.out.println("  the last character never arrived");
                    }
                } catch (SocketTimeoutException e) {
                    System.out.println("  the client waited 400 ms for a byte that was never sent");
                }
            }
            server.join();
        }
        System.out.println("  no status code said so, in either direction");
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
