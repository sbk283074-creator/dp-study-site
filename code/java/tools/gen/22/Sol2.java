import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class Sol2 {
    static final String HEADER = "# quill-2";

    static void ensureHeader(Path file) throws IOException {
        if (Files.exists(file) && !Files.readString(file, StandardCharsets.UTF_8).isEmpty()) {
            return;
        }
        Files.writeString(file, HEADER + "\n", StandardCharsets.UTF_8);
    }

    static long lines(Path p) throws IOException {
        return Files.readAllLines(p, StandardCharsets.UTF_8).size();
    }

    public static void main(String[] args) throws IOException {
        Path file = Path.of("sol2-vault", "notes.tsv");
        Files.createDirectories(file.getParent());

        ensureHeader(file);
        System.out.println("after the first call  = " + lines(file) + " line(s)");
        ensureHeader(file);
        System.out.println("after the second call = " + lines(file) + " line(s)");
        System.out.println("header                = "
                + Files.readAllLines(file, StandardCharsets.UTF_8).get(0));
    }
}
