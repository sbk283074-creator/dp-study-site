import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class Uri {
    public static void main(String[] args) {
        String[] targets = {
            "/",
            "/notes",
            "/notes?tag=work&page=2",
            "/notes?q=hello%20world",
            "/notes?q=hello+world",
        };

        System.out.printf("%-26s %-10s %s%n", "target", "path", "rawQuery");
        for (String target : targets) {
            URI uri = URI.create(target);
            System.out.printf("%-26s %-10s %s%n", target, uri.getPath(), uri.getRawQuery());
        }

        System.out.println();
        System.out.println("q=hello%20world -> '" + decode("hello%20world") + "'");
        System.out.println("q=hello+world   -> '" + decode("hello+world") + "'");
        System.out.println("both spellings decode to the same value: + means space in a query string");

        System.out.println();
        URI smuggled = URI.create("/notes/a%2Fb");
        System.out.println("/notes/a%2Fb -> getPath()    = " + smuggled.getPath());
        System.out.println("             -> getRawPath() = " + smuggled.getRawPath());
        System.out.println("the decoded path contains a separator that was never in the request");
    }

    static String decode(String value) {
        return URLDecoder.decode(value, StandardCharsets.UTF_8);
    }
}
