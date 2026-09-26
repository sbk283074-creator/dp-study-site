cat > Sol2.java <<'JAVA'
public class Sol2 {
    public static void main(String[] args) {
        String weak = Cookies.setCookie("sid", "abc123", null, false, false, null, -1);
        String strong = Cookies.setCookie("sid", "abc123", "/", true, true, "Lax", 3600);
        System.out.println("weak   : " + weak);
        System.out.println("strong : " + strong);
        System.out.println();
        System.out.println("the weak one is readable by any script on the page, is sent over");
        System.out.println("plain HTTP, and is attached to requests other sites initiate. The");
        System.out.println("strong one is none of those things, and it costs one more string");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
