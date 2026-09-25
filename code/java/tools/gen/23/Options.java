import java.nio.file.Path;
import java.util.Arrays;

public class Options {
    record Invocation(Path home, String[] rest) {}

    static Invocation parse(String[] args) {
        Path home = Path.of("vault");
        int i = 0;
        while (i < args.length) {
            if (args[i].equals("--vault")) {
                if (i + 1 == args.length) {
                    throw new IllegalArgumentException("--vault needs a directory");
                }
                home = Path.of(args[i + 1]);
                i += 2;
            } else if (args[i].equals("--")) {
                i++;
                break;
            } else {
                break;
            }
        }
        return new Invocation(home, Arrays.copyOfRange(args, i, args.length));
    }
}
