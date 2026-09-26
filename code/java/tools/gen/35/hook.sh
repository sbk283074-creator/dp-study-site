cat > JvmHook.java <<'JAVA'
public class JvmHook {
    public static void main(String[] args) {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("  hook: flushing the log");
            System.out.println("  hook: closing the database");
        }));
        System.out.println("main: starting");
        System.out.println("main: about to call System.exit(0)");
        System.exit(0);
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out JvmHook.java
java -cp out JvmHook
echo "exit status: $?"
