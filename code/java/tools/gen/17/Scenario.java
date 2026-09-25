import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Stream;

public class Scenario {
    static void write(Path p, String text) throws IOException {
        Files.createDirectories(p.getParent());
        Files.writeString(p, text);
    }

    public static void main(String[] args) throws IOException {
        Path vault = Path.of("vault");
        write(vault.resolve("readme.md"), "# vault\n");
        write(vault.resolve("notes/alpha.md"), "alpha\n");
        write(vault.resolve("notes/beta.md"), "beta\n");
        write(vault.resolve("data/rows.csv"), "a,b\n");
        write(vault.resolve("data/rows2.csv"), "c,d\n");
        write(vault.resolve("bin/tool.txt"), "x\n");

        List<Path> files;
        try (Stream<Path> paths = Files.walk(vault)) {
            files = paths.filter(Files::isRegularFile).sorted().toList();
        }
        for (Path p : files) {
            System.out.println("file  = " + vault.relativize(p));
        }

        Map<String, Integer> byExt = new TreeMap<>();
        long bytes = 0;
        for (Path p : files) {
            String name = p.getFileName().toString();
            String ext = name.contains(".") ? name.substring(name.indexOf('.') + 1) : "(none)";
            byExt.merge(ext, 1, Integer::sum);
            bytes += Files.size(p);
        }
        System.out.println("byExt = " + byExt);
        System.out.println("files = " + files.size());
        System.out.println("bytes = " + bytes);

        try (Stream<Path> top = Files.list(vault)) {
            System.out.println("shallow = " + top.filter(Files::isRegularFile).count());
        }

        try (Stream<Path> paths = Files.walk(vault)) {
            System.out.println("dirs  = " + paths.filter(Files::isDirectory).count());
        }
    }
}
