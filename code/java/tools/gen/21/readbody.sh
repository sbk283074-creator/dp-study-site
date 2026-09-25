cat > ReadBody.java <<'JAVA'
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class ReadBody {
    static List<String> readAll(BufferedReader in) throws IOException {
        List<String> lines = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            lines.add(line);
        }
        return lines;
    }

    public static void main(String[] args) throws IOException {
        List<String> lines = readAll(new BufferedReader(new InputStreamReader(System.in)));
        System.out.println("title     = " + args[0]);
        System.out.println("lines     = " + lines.size());
        for (String line : lines) {
            System.out.println("  | '" + line + "'");
        }
        System.out.println("body      = " + String.join("\n", lines).length() + " character(s)");
    }
}
JAVA

javac -Xlint:all -Werror --release 21 ReadBody.java
printf 'milk and eggs\nbread\n\n' | java -cp . ReadBody Groceries
echo "  -> exit $?"
