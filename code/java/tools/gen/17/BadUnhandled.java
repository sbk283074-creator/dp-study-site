import java.nio.file.Files;
import java.nio.file.Path;

public class BadUnhandled {
    public static void main(String[] args) {
        Files.readString(Path.of("notes.txt"));
    }
}
