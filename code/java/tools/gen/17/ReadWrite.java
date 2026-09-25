import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class ReadWrite {
    public static void main(String[] args) throws IOException {
        Path file = Path.of("notes.txt");

        Files.writeString(file, "first\nsecond\n");
        System.out.println("exists  = " + Files.exists(file));
        System.out.println("size    = " + Files.size(file));
        System.out.println("content = " + Files.readString(file).replace("\n", "|"));

        Files.writeString(file, "appended\n", StandardCharsets.UTF_8,
                StandardOpenOption.APPEND);
        System.out.println("lines   = " + Files.readAllLines(file));
        System.out.println("sizeNow = " + Files.size(file));
    }
}
