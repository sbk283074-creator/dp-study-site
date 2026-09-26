cat > Scenario.java <<'JAVA'
import java.util.LinkedHashMap;
import java.util.Map;

public class Scenario {
    public static void main(String[] args) throws Exception {
        Map<String, String> users = new LinkedHashMap<>();
        byte[] salt = Secrets.salt();
        users.put("bob", Secrets.derive("hunter2", salt, 4096));

        System.out.println("--- a login that stores a hash, not a password ---");
        System.out.println("  stored for bob : <" + users.get("bob").length()
                + " hex chars, and none of them is the password>");
        System.out.println("  correct        : "
                + users.get("bob").equals(Secrets.derive("hunter2", salt, 4096)));
        System.out.println("  wrong          : "
                + users.get("bob").equals(Secrets.derive("hunter3", salt, 4096)));
        System.out.println("  length         : " + users.get("bob").length() + " hex chars");

        System.out.println();
        System.out.println("--- and a cookie the browser will actually protect ---");
        String cookie = Cookies.setCookie("sid", Ids.newId(), "/", true, true, "Lax", 3600);
        String shown = cookie.substring(0, cookie.indexOf('=') + 1) + "<32 hex chars>"
                + cookie.substring(cookie.indexOf(';'));
        System.out.println("  " + shown);
        System.out.println();
        System.out.println("  HttpOnly is present : " + cookie.contains("HttpOnly"));
        System.out.println("  Secure is present   : " + cookie.contains("Secure"));
        System.out.println("  SameSite=Lax        : " + cookie.contains("SameSite=Lax"));
        System.out.println("  expires in seconds  : 3600");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
