cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) throws InterruptedException {
        Object alpha = new Object();
        Object beta = new Object();

        Thread one = new Thread(() -> ordered(alpha, beta));
        Thread two = new Thread(() -> ordered(alpha, beta));
        one.start();
        two.start();
        one.join(5_000);
        two.join(5_000);

        System.out.println("both threads took alpha then beta");
        System.out.println("  t1 finished : " + !one.isAlive());
        System.out.println("  t2 finished : " + !two.isAlive());
        System.out.println();
        System.out.println("a deadlock needs a cycle. If every thread agrees on the order");
        System.out.println("in which locks are taken, no cycle can exist, and it does not");
        System.out.println("matter how many threads or how many locks are involved");
    }

    static void ordered(Object first, Object second) {
        synchronized (first) {
            Nap.millis(100);
            synchronized (second) {
                Nap.millis(10);
            }
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
