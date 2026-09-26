import java.util.Map;

public class AuthDemo {
    public static void main(String[] args) throws Exception {
        System.out.println("--- published test vectors, so this is checkable ---");
        System.out.println();
        System.out.println("  PBKDF2-HMAC-SHA256, password/salt, c=1:");
        System.out.println("    " + Secrets.derive("password", "salt".getBytes("UTF-8"), 1));
        System.out.println("  PBKDF2-HMAC-SHA256, password/salt, c=4096:");
        System.out.println("    " + Secrets.derive("password", "salt".getBytes("UTF-8"), 4096));
        System.out.println("  SHA-256(\"abc\"):");
        System.out.println("    " + Secrets.sha256("abc"));

        System.out.println();
        System.out.println("--- one password, two users, two salts ---");
        byte[] alice = Secrets.salt();
        byte[] bob = Secrets.salt();
        String forAlice = Secrets.derive("correct horse", alice, 4096);
        String forBob = Secrets.derive("correct horse", bob, 4096);
        System.out.println("  same password, different salt, same record : "
                + forAlice.equals(forBob));
        System.out.println("  both verify against their own salt         : "
                + (forAlice.equals(Secrets.derive("correct horse", alice, 4096))
                && forBob.equals(Secrets.derive("correct horse", bob, 4096))));
        System.out.println("  a wrong password verifies                  : "
                + forAlice.equals(Secrets.derive("correct hoarse", alice, 4096)));

        System.out.println();
        System.out.println("--- comparing a secret, and how much that leaks ---");
        String stored = "s3cr3t-session-id";
        String early = "aaaaaaaaaaaaaaaaa";
        String late = "s3cr3t-session-iX";
        System.out.println("  String.equals, differs at index 0   : compared "
                + Secrets.countEquals(stored, early));
        System.out.println("  String.equals, differs at the end   : compared "
                + Secrets.countEquals(stored, late));
        Secrets.equalsAlways(stored, early);
        System.out.println("  equal-time,   differs at index 0    : compared "
                + Secrets.compared);
        Secrets.equalsAlways(stored, late);
        System.out.println("  equal-time,   differs at the end    : compared "
                + Secrets.compared);

        System.out.println();
        System.out.println("--- session ids ---");
        System.out.println("  bytes of entropy : 16");
        System.out.println("  hex characters   : " + Ids.newId().length());
        System.out.println("  distinct in 1000 : " + Ids.distinctIn(1000));
        System.out.println("  new Random, same seed, same value : "
                + Ids.seededPredictably(42));

        System.out.println();
        System.out.println("--- the two headers are not the same shape ---");
        String response = Cookies.setCookie("sid", "abc123", "/", true, true, "Lax", 3600);
        System.out.println("  Set-Cookie : " + response);
        Map<String, String> parsed = Cookies.parse(response);
        System.out.println("  parsed as cookies      : " + parsed.size() + " entries");
        System.out.println("  a request would send   : "
                + Cookies.parse("sid=abc123; theme=dark"));
    }
}
