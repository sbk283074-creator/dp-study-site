import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

public class ReaderLines {
    public static void main(String[] args) throws IOException {
        String text = "first\n\nthird\n";

        int count = 0;
        try (BufferedReader reader = new BufferedReader(new StringReader(text))) {
            String line;
            while ((line = reader.readLine()) != null) {
                count++;
                System.out.printf("%d: '%s' (length %d)%n", count, line, line.length());
            }
        }

        System.out.println("lines = " + count);
        System.out.println("the blank line was a line; the trailing newline was not");
    }
}
