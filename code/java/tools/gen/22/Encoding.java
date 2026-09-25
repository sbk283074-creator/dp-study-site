import java.nio.charset.StandardCharsets;

public class Encoding {
    static int count(byte[] bytes, byte target) {
        int n = 0;
        for (byte b : bytes) {
            if (b == target) {
                n++;
            }
        }
        return n;
    }

    public static void main(String[] args) {
        String body = "café — 咖啡";

        byte[] utf8 = body.getBytes(StandardCharsets.UTF_8);
        byte[] latin1 = body.getBytes(StandardCharsets.ISO_8859_1);

        System.out.println("characters    = " + body.length());
        System.out.println("UTF-8 bytes   = " + utf8.length);
        System.out.println("Latin-1 bytes = " + latin1.length);
        System.out.println("Latin-1 '?'   = " + count(latin1, (byte) '?'));
        System.out.println();
        System.out.println("UTF-8 round trip   = "
                + new String(utf8, StandardCharsets.UTF_8).equals(body));
        System.out.println("Latin-1 round trip = "
                + new String(latin1, StandardCharsets.ISO_8859_1).equals(body));
    }
}
