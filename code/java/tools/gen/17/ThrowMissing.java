import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class ThrowMissing {
    public static void main(String[] args) throws IOException {
        Files.readString(Path.of("nope.txt"));
    }
}
