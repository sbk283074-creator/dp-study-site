import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class Scenario {
    static void show(String line) {
        String body = line.split("\t", 3)[2];
        System.out.printf("body='%s' length=%d endsWithCR=%b%n",
                body.replace("\r", "\\r"), body.length(), body.endsWith("\r"));
    }

    public static void main(String[] args) throws Exception {
        Path file = Path.of("exported.tsv");
        Files.writeString(file, "1\tGroceries\tmilk and eggs\r\n2\tReading\tchapter 21\r\n",
                StandardCharsets.UTF_8);

        System.out.println("-- Files.readAllLines --");
        for (String line : Files.readAllLines(file, StandardCharsets.UTF_8)) {
            show(line);
        }

        System.out.println();
        System.out.println("-- Files.readString and split --");
        for (String line : Files.readString(file, StandardCharsets.UTF_8).split("\n")) {
            if (!line.isEmpty()) {
                show(line);
            }
        }
    }
}
