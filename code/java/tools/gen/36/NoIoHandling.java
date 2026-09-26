import java.net.URI;

public class NoIoHandling {
    public static void main(String[] args) {
        URI.create("http://127.0.0.1:8080/healthz")
                .toURL()
                .openConnection()
                .getInputStream()
                .readAllBytes();
    }
}
