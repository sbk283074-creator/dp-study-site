import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class RawExchange {
    static final String REQUEST =
            "GET /notes HTTP/1.1\r\n"
            + "Host: localhost\r\n"
            + "Accept: text/plain\r\n"
            + "\r\n";

    static final String RESPONSE =
            "HTTP/1.1 200 OK\r\n"
            + "Content-Type: text/plain; charset=utf-8\r\n"
            + "Content-Length: 12\r\n"
            + "Connection: close\r\n"
            + "\r\n"
            + "hello, world";

    public static void main(String[] args) throws Exception {
        String[] serverSaw = new String[1];

        try (ServerSocket listener = new ServerSocket(0)) {
            Thread server = new Thread(() -> {
                try (Socket socket = listener.accept()) {
                    serverSaw[0] = readHead(socket.getInputStream());
                    OutputStream out = socket.getOutputStream();
                    out.write(RESPONSE.getBytes(StandardCharsets.US_ASCII));
                    out.flush();
                } catch (IOException e) {
                    throw new java.io.UncheckedIOException(e);
                }
            });
            server.start();

            String clientSaw;
            try (Socket socket = new Socket("127.0.0.1", listener.getLocalPort())) {
                OutputStream out = socket.getOutputStream();
                out.write(REQUEST.getBytes(StandardCharsets.US_ASCII));
                out.flush();
                clientSaw = readToEnd(socket.getInputStream());
            }
            server.join();

            System.out.println("-- what the server read, byte for byte --");
            System.out.print(show(serverSaw[0]));
            System.out.println();
            System.out.println("-- what the client read, byte for byte --");
            System.out.print(show(clientSaw));
        }
    }

    /** Reads up to and including the blank line that ends the request head. */
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

    /** Reads until the other end closes -- the only signal HTTP/1.0 had. */
    static String readToEnd(InputStream in) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        in.transferTo(bytes);
        return bytes.toString(StandardCharsets.US_ASCII);
    }

    /** Makes the line structure visible instead of letting CRLF act on the terminal. */
    static String show(String text) {
        if (text.endsWith("\r\n")) {
            text = text.substring(0, text.length() - 2);
        }
        StringBuilder out = new StringBuilder();
        for (String line : text.split("\r\n", -1)) {
            out.append(line.isEmpty() ? "|" : "| " + line).append('\n');
        }
        return out.toString();
    }
}
