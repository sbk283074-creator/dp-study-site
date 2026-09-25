import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

public class Lines {
    public static void main(String[] args) throws IOException {
        Path log = Path.of("app.log");
        Files.write(log, List.of(
                "2026-01-01 INFO  started",
                "2026-01-01 WARN  disk 91% full",
                "2026-01-01 ERROR write failed",
                "2026-01-02 INFO  started"));

        System.out.println("all lines = " + Files.readAllLines(log).size());

        try (Stream<String> lines = Files.lines(log)) {
            System.out.println("warnings  = " + lines.filter(l -> l.contains("WARN")).count());
        }

        try (Stream<String> lines = Files.lines(log)) {
            lines.map(l -> l.split("\\s+", 3)[1])
                 .distinct()
                 .sorted()
                 .forEach(level -> System.out.println("level     = " + level));
        }
    }
}
