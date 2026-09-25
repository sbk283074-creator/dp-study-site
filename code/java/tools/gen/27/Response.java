import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/** A response as a value: nothing is written until something asks for the bytes. */
public record Response(int status, String contentType, String body) {

    static final String TEXT = "text/plain; charset=utf-8";

    public static Response text(int status, String body) {
        return new Response(status, TEXT, body);
    }

    public static Response ok(String body) {
        return text(200, body);
    }

    public static Response notFound(String path) {
        return text(404, "no route for " + path);
    }

    public static Response methodNotAllowed(String method, String allow) {
        return text(405, method + " is not allowed; try " + allow);
    }

    /** The length of the body as bytes, which is what the wire needs. */
    public int length() {
        return body.getBytes(StandardCharsets.UTF_8).length;
    }

    /** The one place that turns a response value into a framed HTTP response. */
    public void writeTo(com.sun.net.httpserver.HttpExchange exchange) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", contentType);
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }
}
