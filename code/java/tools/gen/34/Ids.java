import java.security.SecureRandom;
import java.util.HashSet;
import java.util.Random;
import java.util.Set;

/** Where session ids come from, and why `new Random()` is the wrong answer. */
public final class Ids {

    private static final SecureRandom RANDOM = new SecureRandom();

    private Ids() {
    }

    public static String newId() {
        byte[] bytes = new byte[16];
        RANDOM.nextBytes(bytes);
        StringBuilder out = new StringBuilder();
        for (byte b : bytes) {
            out.append(Character.forDigit((b >> 4) & 0xf, 16));
            out.append(Character.forDigit(b & 0xf, 16));
        }
        return out.toString();
    }

    public static int distinctIn(int draws) {
        Set<String> seen = new HashSet<>();
        for (int i = 0; i < draws; i++) {
            seen.add(newId());
        }
        return seen.size();
    }

    /** Two `Random`s built from the same seed produce the same sequence. Always. */
    public static boolean seededPredictably(long seed) {
        Random a = new Random(seed);
        Random b = new Random(seed);
        return a.nextLong() == b.nextLong();
    }
}
