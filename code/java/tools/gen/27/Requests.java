import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * The adapter. This is the only file in the service that knows about both an HttpExchange and a
 * Request, and it is deliberately the only one: nothing downstream can reach the socket.
 */
public final class Requests {
    private Requests() {}

    public static Request from(HttpExchange exchange) throws IOException {
        Map<String, String> headers = new LinkedHashMap<>();
        exchange.getRequestHeaders()
                .forEach((name, values) -> headers.put(name, String.join(", ", values)));
        return new Request(
                exchange.getRequestMethod(),
                exchange.getRequestURI().getPath(),
                Query.parse(exchange.getRequestURI().getRawQuery()),
                headers,
                new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8),
                Map.of());
    }
}
