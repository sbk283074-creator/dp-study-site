cat > Sol2.java <<'JAVA'
public class Sol2 {
    public static void main(String[] args) {
        Log log = new Log("warn");
        log.line("debug", "not kept");
        log.line("info", "also not kept");
        log.line("warn", "kept", "path", "/notes");
        log.line("error", "kept", "path", "/notes");
        System.out.println("written  : " + log.written());
        System.out.println("info on  : " + log.enabled("info"));
        System.out.println("warn on  : " + log.enabled("warn"));
        System.out.println();
        System.out.println("the threshold is a floor, not a filter list: everything at or");
        System.out.println("above it is kept, and that is why the order of the levels matters");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
