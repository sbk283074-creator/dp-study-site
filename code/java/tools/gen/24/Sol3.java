import java.nio.file.Files;
import java.nio.file.Path;

public class Sol3 {
    public static void main(String[] args) throws Exception {
        Path home = Path.of("sol3-vault");
        Vault vault = new Vault(home);

        String body = "line one\nline two\nline three";
        Note note = new Note(vault.nextId(), "Multi-line", body);
        vault.append(note);

        System.out.println("in memory  = " + note.body().length() + " character(s), "
                + note.body().split("\n").length + " line(s)");
        System.out.println("on disk    = "
                + Files.readAllLines(vault.file()).size() + " line(s)");
        System.out.println("read back  = " + vault.read().get(0).equals(note));
    }
}
