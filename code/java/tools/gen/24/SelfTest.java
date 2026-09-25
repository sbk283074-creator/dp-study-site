import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class SelfTest {
    record Case(String label, String[] rest, String stdin, int expected) {}

    public static void main(String[] args) throws Exception {
        Path home = Files.createTempDirectory("quill-selftest");

        List<Case> cases = List.of(
            new Case("(none)", new String[] {}, "", 0),
            new Case("list", new String[] {"list"}, "", 0),
            new Case("add Groceries", new String[] {"add", "Groceries"}, "milk and eggs\n", 0),
            new Case("list", new String[] {"list"}, "", 0),
            new Case("show 1", new String[] {"show", "1"}, "", 0),
            new Case("show 2", new String[] {"show", "2"}, "", 5),
            new Case("delete 1", new String[] {"delete", "1"}, "", 0),
            new Case("delete 1", new String[] {"delete", "1"}, "", 5),
            new Case("show seven", new String[] {"show", "seven"}, "", 2),
            new Case("frobnicate", new String[] {"frobnicate"}, "", 2));

        int passed = 0;
        for (Case c : cases) {
            int actual = Main.run(withHome(home, c.rest()),
                    new BufferedReader(new StringReader(c.stdin())), sink(), sink());
            boolean ok = actual == c.expected();
            if (ok) {
                passed++;
            }
            System.out.printf("%-16s expected %d, got %d  %s%n",
                    c.label(), c.expected(), actual, ok ? "ok" : "FAIL");
        }

        System.out.println();
        System.out.println("passed " + passed + " of " + cases.size());
    }

    static String[] withHome(Path home, String[] rest) {
        String[] full = new String[rest.length + 2];
        full[0] = "--vault";
        full[1] = home.toString();
        System.arraycopy(rest, 0, full, 2, rest.length);
        return full;
    }

    static PrintStream sink() {
        return new PrintStream(new ByteArrayOutputStream());
    }
}
