import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class Scenario {
    static List<String> entries(Path dir) throws Exception {
        try (var stream = Files.list(dir)) {
            return stream.map(p -> p.getFileName().toString()).sorted().toList();
        }
    }

    public static void main(String[] args) throws Exception {
        Path work = Path.of("scenario-work");
        Files.createDirectories(work);

        Path leaked = work.resolve("vault");
        Files.createDirectories(leaked);
        System.out.println("after a test with no --vault, " + work.getFileName()
                + " contains " + entries(work));

        Files.delete(leaked);
        System.out.println("after a test with --vault,    " + work.getFileName()
                + " contains " + entries(work));

        System.out.println();
        System.out.println("the first run left state behind that the second run would have found");
    }
}
