import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class Attributes {
    public static void main(String[] args) throws IOException {
        Path dir = Path.of("data");
        Path file = dir.resolve("report.csv");

        Files.createDirectories(dir);
        Files.writeString(file, "a,b\n1,2\n");

        System.out.println("exists     = " + Files.exists(file));
        System.out.println("regular    = " + Files.isRegularFile(file));
        System.out.println("directory  = " + Files.isDirectory(dir));
        System.out.println("size       = " + Files.size(file));
        System.out.println("readable   = " + Files.isReadable(file));
        System.out.println("lines      = " + Files.readAllLines(file).size());

        Files.createDirectories(dir);
        System.out.println("idempotent = " + Files.isDirectory(dir));
    }
}
