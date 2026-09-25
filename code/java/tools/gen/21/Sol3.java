import java.io.BufferedReader;
import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.List;

public class Sol3 {
    static final int MAX_LINES = 3;

    static BufferedReader reader(String text) {
        return new BufferedReader(new StringReader(text));
    }

    static List<String> readAtMost(BufferedReader in, int limit) throws IOException {
        List<String> lines = new ArrayList<>();
        String line;
        while ((line = in.readLine()) != null) {
            if (lines.size() == limit) {
                throw new IllegalStateException("more than " + limit + " lines");
            }
            lines.add(line);
        }
        return lines;
    }

    public static void main(String[] args) throws IOException {
        try {
            System.out.println("three lines: " + readAtMost(reader("a\nb\nc\n"), MAX_LINES));
        } catch (IllegalStateException e) {
            System.out.println("three lines: " + e.getMessage());
        }

        try {
            System.out.println("four lines:  " + readAtMost(reader("a\nb\nc\nd\n"), MAX_LINES));
        } catch (IllegalStateException e) {
            System.out.println("four lines:  " + e.getMessage());
        }

        System.out.println();
        System.out.println("the limit is checked before the line is added, so at most 3 means 3");
    }
}
