import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;

public class Walk {
    public static void main(String[] args) throws IOException {
        Path root = Path.of("vault");
        Files.createDirectories(root.resolve("notes/2026"));
        Files.createDirectories(root.resolve("notes/2025"));
        Files.writeString(root.resolve("readme.md"), "top\n");
        Files.writeString(root.resolve("notes/2026/jan.md"), "jan\n");
        Files.writeString(root.resolve("notes/2025/dec.md"), "dec\n");

        try (Stream<Path> paths = Files.walk(root)) {
            paths.filter(Files::isRegularFile)
                 .map(root::relativize)
                 .map(Path::toString)
                 .sorted()
                 .forEach(p -> System.out.println("file  = " + p));
        }

        try (Stream<Path> paths = Files.list(root)) {
            paths.map(p -> p.getFileName().toString())
                 .sorted()
                 .forEach(p -> System.out.println("child = " + p));
        }

        try (Stream<Path> paths = Files.walk(root)) {
            System.out.println("depth = " + paths.count());
        }
    }
}
