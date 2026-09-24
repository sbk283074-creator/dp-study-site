import java.util.Map;
import java.util.Optional;

public class Sol3 {

    static final Map<String, String> CONFIG =
            Map.of("host", "example.com", "port", "8080");

    static Optional<String> raw(String key) {
        return Optional.ofNullable(CONFIG.get(key));
    }

    static Optional<Integer> port() {
        return raw("port").map(Integer::parseInt);
    }

    public static void main(String[] args) {
        System.out.println("host: " + raw("host").orElse("localhost"));
        System.out.println("missing key: " + raw("timeout").orElse("30"));
        System.out.println("port: " + port());
        System.out.println("port or default: " + port().orElse(80));
        System.out.println("filtered: " + port().filter(p -> p > 1024).map(p -> "above 1024"));
        System.out.println("a deferred default: " + raw("timeout").orElseGet(() -> "computed-30"));
    }
}
