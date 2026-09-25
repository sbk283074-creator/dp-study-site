import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

public class Vault {
    static final String FILE = "notes.tsv";

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
        List<Note> notes = new ArrayList<>();
        for (String line : Files.readAllLines(file(), StandardCharsets.UTF_8)) {
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
        Files.writeString(file(), note.render() + "\n", StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }
}
