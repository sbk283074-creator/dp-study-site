import java.nio.file.Files;
import java.nio.file.Path;

public class VaultDemo {
    public static void main(String[] args) throws Exception {
        Path home = Path.of("demo-vault");
        Vault vault = new Vault(home);

        System.out.println("empty        = " + vault.read());

        vault.append(new Note(vault.nextId(), "Groceries", "milk and eggs"));
        vault.append(new Note(vault.nextId(), "Reading", "chapter 20"));

        System.out.println("after two    = " + vault.read().size() + " note(s)");
        System.out.println("next id      = " + vault.nextId());
        System.out.println();
        System.out.println("notes.tsv, tabs shown as \\t:");
        System.out.print(Files.readString(home.resolve("notes.tsv")).replace("\t", "\\t"));
        System.out.println();
        System.out.println("lines on disk= "
                + Files.readAllLines(home.resolve("notes.tsv")).size());
    }
}
