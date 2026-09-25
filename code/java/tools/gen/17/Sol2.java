import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Sol2 {
    public static void main(String[] args) throws IOException {
        Path dir = Path.of("src");
        Files.createDirectories(dir);
        Files.write(dir.resolve("a.txt"), List.of("one two", "three"));
        Files.write(dir.resolve("b.txt"), List.of("four", "five six", "seven"));

        List<Path> files;
        try (var paths = Files.list(dir)) {
            files = paths.sorted().toList();
        }

        Map<String, Integer> words = new TreeMap<>();
        for (Path p : files) {
            int count = Files.readAllLines(p).stream()
                    .mapToInt(line -> line.split("\\s+").length)
                    .sum();
            words.put(p.getFileName().toString(), count);
        }
        System.out.println("words = " + words);
        System.out.println("total = " + words.values().stream().mapToInt(Integer::intValue).sum());
    }
}
