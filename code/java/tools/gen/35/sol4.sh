cat > Sol4.java <<'JAVA'
public class Sol4 {
    public static void main(String[] args) {
        Hooks hooks = new Hooks();
        hooks.add(() -> System.out.println("  first registered, last run"));
        hooks.add(() -> System.out.println("  last registered, first run"));
        hooks.run();
        hooks.run();
        System.out.println("stopped : " + hooks.stopped());
        System.out.println();
        System.out.println("reverse order mirrors try-with-resources, so the thing that was");
        System.out.println("opened first closes last. Running twice does nothing the second");
        System.out.println("time, because a shutdown hook that can run twice can also double");
        System.out.println("free a resource that was only ever acquired once");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
