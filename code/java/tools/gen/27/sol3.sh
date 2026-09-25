cat > Sol3.java <<'EOF'
import java.util.List;

public class Sol3 {
    public static void main(String[] args) {
        Router router = new Router();
        router.get("/notes", request -> Response.ok("every note"));

        for (String path : List.of("/notes", "/notes/", "//notes", "/NOTES", "/notes/ ")) {
            Response response = router.route(new Request("GET", path, ""));
            System.out.printf("%-12s -> %d  '%s'%n", "'" + path + "'", response.status(),
                    response.body());
        }

        System.out.println();
        System.out.println("'/notes/' matched, because split() drops a trailing empty segment");
        System.out.println("'//notes' did not, because only the trailing one is dropped");
        System.out.println("and matching is case-sensitive, so '/NOTES' is a different path");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
