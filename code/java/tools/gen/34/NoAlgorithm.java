import java.security.MessageDigest;

public class NoAlgorithm {
    public static void main(String[] args) {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        System.out.println(digest.getDigestLength());
    }
}
