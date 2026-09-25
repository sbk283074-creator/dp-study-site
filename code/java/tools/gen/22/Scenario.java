import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

public class Scenario {
    static long size(Path p) throws Exception {
        return Files.size(p);
    }

    static long lines(Path p) throws Exception {
        return Files.readAllLines(p, StandardCharsets.UTF_8).size();
    }

    public static void main(String[] args) throws Exception {
        Path dir = Path.of("scenario-vault");
        Path live = dir.resolve("notes.tsv");
        Path temp = dir.resolve("notes.tsv.tmp");
        Files.createDirectories(dir);

        String before = "# quill-2\n1\tGroceries\tmilk and eggs\n";
        String after = before + "2\tReading\tchapter 22\n";
        Files.writeString(live, before, StandardCharsets.UTF_8);

        System.out.println("before the append     : " + size(live) + " bytes, "
                + lines(live) + " line(s)");

        Files.writeString(live, "", StandardCharsets.UTF_8);
        System.out.println("mid-write, truncated  : " + size(live) + " bytes, "
                + lines(live) + " line(s)");

        Files.writeString(temp, after, StandardCharsets.UTF_8);
        Files.move(temp, live, StandardCopyOption.ATOMIC_MOVE,
                StandardCopyOption.REPLACE_EXISTING);
        System.out.println("after the atomic move : " + size(live) + " bytes, "
                + lines(live) + " line(s)");
        System.out.println("temp file left behind : " + Files.exists(temp));
    }
}
