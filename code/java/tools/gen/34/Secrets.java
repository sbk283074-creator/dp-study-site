import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.HexFormat;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/** Passwords: a per-user salt, a slow key-derivation function, and an equal-time compare. */
public final class Secrets {

    private static final SecureRandom RANDOM = new SecureRandom();
    public static int compared;

    private Secrets() {
    }

    public static byte[] salt() {
        byte[] bytes = new byte[16];
        RANDOM.nextBytes(bytes);
        return bytes;
    }

    public static String derive(String password, byte[] salt, int iterations) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, 256);
        byte[] key = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                .generateSecret(spec).getEncoded();
        return HexFormat.of().formatHex(key);
    }

    public static String sha256(String text) throws Exception {
        return HexFormat.of().formatHex(
                MessageDigest.getInstance("SHA-256").digest(text.getBytes("UTF-8")));
    }

    /** `String.equals` stops at the first difference, and the count is observable. */
    public static int countEquals(String a, String b) {
        int seen = 0;
        int limit = Math.min(a.length(), b.length());
        for (int i = 0; i < limit; i++) {
            seen++;
            if (a.charAt(i) != b.charAt(i)) {
                return seen;
            }
        }
        return seen;
    }

    /** Reads every character whether or not it has already found a difference. */
    public static boolean equalsAlways(String a, String b) {
        compared = 0;
        if (a.length() != b.length()) {
            return false;
        }
        int difference = 0;
        for (int i = 0; i < a.length(); i++) {
            compared++;
            difference |= a.charAt(i) ^ b.charAt(i);
        }
        return difference == 0;
    }
}
