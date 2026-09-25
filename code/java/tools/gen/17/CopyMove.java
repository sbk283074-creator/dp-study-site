import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;

public class CopyMove {
    public static void main(String[] args) throws IOException {
        Path src = Path.of("a.txt");
        Path dst = Path.of("sub/b.txt");
        Files.writeString(src, "hello\n");
        Files.createDirectories(dst.getParent());

        Files.copy(src, dst);
        System.out.println("copied     = " + Files.exists(dst));
        System.out.println("content    = " + Files.readString(dst).strip());

        try {
            Files.copy(src, dst);
        } catch (FileAlreadyExistsException e) {
            System.out.println("again      = " + e.getClass().getSimpleName());
        }

        Files.move(dst, Path.of("sub/c.txt"));
        System.out.println("movedFrom  = " + Files.exists(dst));
        System.out.println("movedTo    = " + Files.exists(Path.of("sub/c.txt")));

        Files.delete(Path.of("sub/c.txt"));
        System.out.println("deleted    = " + Files.exists(Path.of("sub/c.txt")));

        Files.deleteIfExists(Path.of("sub/c.txt"));
        System.out.println("idempotent = " + Files.exists(Path.of("sub/c.txt")));
    }
}
