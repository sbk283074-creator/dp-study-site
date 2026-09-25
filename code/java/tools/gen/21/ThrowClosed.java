import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;

public class ThrowClosed {
    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new StringReader("a\nb\n"));
        reader.close();
        System.out.println("closed the reader, now reading from it");
        System.out.println(reader.readLine());
    }
}
