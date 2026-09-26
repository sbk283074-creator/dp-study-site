cat > Flag.java <<'JAVA'
public class Flag {
    static volatile boolean stop = false;

    public static void main(String[] args) throws InterruptedException {
        Thread reader = new Thread(() -> {
            while (!stop) {
                Thread.onSpinWait();
            }
        });
        reader.start();

        Nap.millis(50);
        stop = true;
        reader.join(2_000);

        System.out.println("reader stopped within 2 s    : " + !reader.isAlive());
        System.out.println();
        System.out.println("a write to a volatile field happens-before every later read");
        System.out.println("of it, so the reader is guaranteed to see this one.");
        System.out.println("Without volatile there is no such guarantee: the read may be");
        System.out.println("hoisted out of the loop, and the thread may never stop.");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Flag.java
java -cp out Flag
