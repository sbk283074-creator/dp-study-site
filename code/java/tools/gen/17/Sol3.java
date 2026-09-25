import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class Sol3 {
    static void writeAtomically(Path target, String content) throws IOException {
        Path dir = target.getParent() == null ? Path.of(".") : target.getParent();
        Files.createDirectories(dir);

        Path tmp = Files.createTempFile(dir, target.getFileName().toString(), ".tmp");
        try {
            Files.writeString(tmp, content);
            Files.move(tmp, target,
                    StandardCopyOption.REPLACE_EXISTING,
                    StandardCopyOption.ATOMIC_MOVE);
        } finally {
            Files.deleteIfExists(tmp);
        }
    }

    public static void main(String[] args) throws IOException {
        Path target = Path.of("store/config.txt");

        writeAtomically(target, "v1\n");
        System.out.println("first  = " + Files.readString(target).strip());

        writeAtomically(target, "v2\n");
        System.out.println("second = " + Files.readString(target).strip());

        try (var leftovers = Files.list(Path.of("store"))) {
            System.out.println("files  = " + leftovers
                    .map(p -> p.getFileName().toString())
                    .sorted()
                    .toList());
        }
    }
}
