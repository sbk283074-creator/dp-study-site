import java.nio.charset.StandardCharsets;

public class Sol3 {
    /** The whole response, as the bytes that go on the wire. */
    static String response(int code, String reason, String contentType, String body) {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        return "HTTP/1.1 " + code + " " + reason + "\r\n"
                + "Content-Type: " + contentType + "\r\n"
                + "Content-Length: " + bytes.length + "\r\n"
                + "\r\n"
                + body;
    }

    static String show(String text) {
        StringBuilder out = new StringBuilder();
        for (String line : text.split("\r\n", -1)) {
            out.append(line.isEmpty() ? "|" : "| " + line).append('\n');
        }
        return out.toString();
    }

    public static void main(String[] args) {
        String body = "caf\u00e9";

        System.out.println("body             = " + body);
        System.out.println("String.length()  = " + body.length());
        System.out.println("UTF-8 byte count = " + body.getBytes(StandardCharsets.UTF_8).length);
        System.out.println();
        System.out.println("the response that writes:");
        System.out.print(show(response(200, "OK", "text/plain; charset=utf-8", body)));
        System.out.println();
        System.out.println("Content-Length counts bytes. String.length() would have said 4, and the");
        System.out.println("client would have stopped one byte early and dropped the second byte of the e.");
    }
}
