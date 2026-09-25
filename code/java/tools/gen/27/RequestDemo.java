import java.util.List;
import java.util.Map;

public class RequestDemo {
    public static void main(String[] args) {
        Request request = new Request("GET", "/notes/7", Map.of("q", List.of("milk")),
                Map.of("accept", "text/plain"), "", Map.of("id", "7"));

        System.out.println("method  " + request.method());
        System.out.println("path    " + request.path());
        System.out.println("var id  " + request.var("id"));
        System.out.println("query q " + request.query("q"));
        System.out.println("accept  " + request.header("Accept"));

        System.out.println();
        System.out.println("asking for a variable the pattern never declared:");
        try {
            request.var("nope");
        } catch (IllegalArgumentException e) {
            System.out.println("  " + e.getMessage());
        }

        System.out.println();
        Request other = request.withVars(Map.of("id", "9"));
        System.out.println("after withVars, the original still says id = " + request.var("id"));
        System.out.println("and the copy says id = " + other.var("id"));
        System.out.println("a record cannot be edited in place, so a handler cannot corrupt another's request");
    }
}
