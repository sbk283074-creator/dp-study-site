import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

public class Vault {
    static final String FILE = "notes.tsv";
    static final String HEADER = "# quill-2";

    private final Path home;

    Vault(Path home) {
        this.home = home;
    }

    Path file() {
        return home.resolve(FILE);
    }

    List<Note> read() throws IOException {
        if (!Files.exists(file())) {
            return List.of();
        }
        List<String> lines = Files.readAllLines(file(), StandardCharsets.UTF_8);
        if (lines.isEmpty()) {
            return List.of();
        }
        if (!lines.get(0).equals(HEADER)) {
            throw new IOException("unsupported vault header: " + lines.get(0));
        }
        List<Note> notes = new ArrayList<>();
        for (String line : lines.subList(1, lines.size())) {
            if (!line.isBlank()) {
                notes.add(Note.parse(line));
            }
        }
        return notes;
    }

    int nextId() throws IOException {
        int highest = 0;
        for (Note note : read()) {
            highest = Math.max(highest, note.id());
        }
        return highest + 1;
    }

    void append(Note note) throws IOException {
        Files.createDirectories(home);
        if (!Files.exists(file())) {
            Files.writeString(file(), HEADER + "\n", StandardCharsets.UTF_8);
        }
        Files.writeString(file(), note.render() + "\n", StandardCharsets.UTF_8,
                StandardOpenOption.APPEND);
    }
}
