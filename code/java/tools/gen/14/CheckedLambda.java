import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.Function;

public class CheckedLambda {

    public static void main(String[] args) {
        Function<Path, String> read = path -> Files.readString(path);
        System.out.println(read.apply(Path.of("missing.txt")));
    }
}
