cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) {
        String hostile = "bob\n2026-09-25 level=error msg=\"breach\" user=admin";
        Log log = new Log("info");
        log.line("info", "login", "user", hostile);
        System.out.println();
        System.out.println("one line in, one line out. An unescaped newline would have made");
        System.out.println("this two lines, and the second one would say whatever the client");
        System.out.println("wanted it to say -- to your log search, your alerting, and the");
        System.out.println("person reading it at three in the morning");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
