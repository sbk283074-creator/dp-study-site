cat > Headers.java <<'JAVA'
import java.util.Map;

public class Headers {
    public static void main(String[] args) {
        String response = Cookies.setCookie("sid", "abc123", "/", true, true, "Lax", 3600);
        System.out.println("Set-Cookie             : " + response);
        System.out.println();
        System.out.println("read back with the request parser:");
        for (Map.Entry<String, String> entry : Cookies.parse(response).entrySet()) {
            System.out.println("  cookie " + entry.getKey() + " = " + entry.getValue());
        }
        System.out.println();
        System.out.println("three of those are not cookies. HttpOnly, Secure and SameSite are");
        System.out.println("attributes that tell the browser what to do with the cookie, and a");
        System.out.println("naive parser stores them as if a client had sent them -- which is");
        System.out.println("how a server ends up believing it was sent a cookie named Path");

        System.out.println();
        System.out.println("each attribute is a promise about one attack:");
        System.out.println("  HttpOnly  : document.cookie cannot read it, so XSS cannot steal it");
        System.out.println("  Secure    : the browser will not send it over plain HTTP");
        System.out.println("  SameSite  : it is not sent on cross-site requests, which is what");
        System.out.println("              stops CSRF without a token");
        System.out.println("  Path      : the cookie is only sent under this prefix");
        System.out.println("  Max-Age   : it expires, in seconds, from now");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Headers.java
java -cp out Headers
