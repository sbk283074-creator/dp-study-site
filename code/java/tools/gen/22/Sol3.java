import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;

public class Sol3 {
    static void rewriteAtomically(Path file, List<String> lines) throws IOException {
        Path temp = file.resolveSibling(file.getFileName() + ".tmp");
        Files.writeString(temp, String.join("\n", lines) + "\n", StandardCharsets.UTF_8);
        Files.move(temp, file, StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
    }

    public static void main(String[] args) throws IOException {
        Path dir = Path.of("sol3-vault");
        Path file = dir.resolve("notes.tsv");
        Files.createDirectories(dir);

        Files.writeString(file, "# quill-2\n1\tGroceries\tmilk\n", StandardCharsets.UTF_8);
        System.out.println("before = " + Files.size(file) + " bytes, "
                + Files.readAllLines(file, StandardCharsets.UTF_8).size() + " line(s)");

        rewriteAtomically(file, List.of("# quill-2", "1\tGroceries\tmilk",
                "2\tReading\tchapter 22"));

        System.out.println("after  = " + Files.size(file) + " bytes, "
                + Files.readAllLines(file, StandardCharsets.UTF_8).size() + " line(s)");
        System.out.println("temp   = " + Files.exists(dir.resolve("notes.tsv.tmp")));
        System.out.println();
        System.out.println("the live file is replaced, never truncated in place");
    }
}
