cat > Sol1.java <<'JAVA'
import java.util.Map;

public class Sol1 {
    public static void main(String[] args) {
        Map<String, String> cookies = Cookies.parse("sid=abc123; theme=dark; lang=en");
        System.out.println("pairs   : " + cookies.size());
        System.out.println("sid     : " + cookies.get("sid"));
        System.out.println("theme   : " + cookies.get("theme"));
        System.out.println("missing : " + cookies.get("nope"));
        System.out.println();
        System.out.println("a missing cookie is null, not \"\", and code that treats the two");
        System.out.println("the same will treat \"logged out\" as \"logged in as \"''");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
