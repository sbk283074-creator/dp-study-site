import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Optional;

public class Sol1 {
    static Optional<String> read(Path p) {
        try {
            return Optional.of(Files.readString(p));
        } catch (NoSuchFileException e) {
            return Optional.empty();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static void main(String[] args) throws IOException {
        Path present = Path.of("present.txt");
        Files.writeString(present, "configured\n");

        System.out.println("present = " + read(present).map(String::strip).orElse("(default)"));
        System.out.println("missing = " + read(Path.of("absent.txt")).orElse("(default)"));
        System.out.println("exists  = " + Files.exists(Path.of("absent.txt")));
    }
}
