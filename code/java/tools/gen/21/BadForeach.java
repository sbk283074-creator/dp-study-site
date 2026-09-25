import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

public class BadForeach {
    public static void main(String[] args) throws IOException {
        try (BufferedReader reader = new BufferedReader(new StringReader("a\nb\n"))) {
            for (String line : reader) {
                System.out.println(line);
            }
        }
    }
}
