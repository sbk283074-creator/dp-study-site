import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

public class Sol4 {
    static final Path FILE = Path.of("sol4-vault", "notes.tsv");

    static List<String> read() throws IOException {
        return Files.exists(FILE)
                ? Files.readAllLines(FILE, StandardCharsets.UTF_8)
                : List.of();
    }

    static void write(List<String> lines) throws IOException {
        Files.createDirectories(FILE.getParent());
        Files.writeString(FILE, String.join("\n", lines) + "\n", StandardCharsets.UTF_8);
    }

    static void append(String line) throws IOException {
        Files.createDirectories(FILE.getParent());
        Files.writeString(FILE, line + "\n", StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }

    static int idByMax() throws IOException {
        int highest = 0;
        for (String line : read()) {
            highest = Math.max(highest, Integer.parseInt(line.split("\t", 2)[0]));
        }
        return highest + 1;
    }

    static int idBySize() throws IOException {
        return read().size() + 1;
    }

    public static void main(String[] args) throws IOException {
        append("1\tGroceries\tmilk and eggs");
        append("2\tReading\tchapter 20");
        append("3\tDraft\tdelete me");
        System.out.println("after three       max+1 = " + idByMax()
                + "   size+1 = " + idBySize());

        List<String> kept = new ArrayList<>();
        for (String line : read()) {
            if (!line.startsWith("2\t")) {
                kept.add(line);
            }
        }
        write(kept);
        System.out.println("after deleting #2 max+1 = " + idByMax()
                + "   size+1 = " + idBySize());
        System.out.println();
        System.out.println("size+1 now names #3, a note that already exists");
    }
}
