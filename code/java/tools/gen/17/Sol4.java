import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.IntStream;

public class Sol4 {
    public static void main(String[] args) throws IOException {
        Path big = Path.of("big.txt");
        Files.write(big, IntStream.range(0, 1000).mapToObj(i -> "line " + i).toList());

        List<String> all = Files.readAllLines(big);
        System.out.println("readAllLines = " + all.size());
        System.out.println("first        = " + all.get(0));
        System.out.println("last         = " + all.get(all.size() - 1));

        try (var lines = Files.lines(big)) {
            System.out.println("stream first = " + lines.findFirst().orElse("none"));
        }

        System.out.println("bytes        = " + Files.size(big));
    }
}
