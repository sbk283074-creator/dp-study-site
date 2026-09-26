cat > Deadlock.java <<'JAVA'
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class Deadlock {
    public static void main(String[] args) throws InterruptedException {
        Object first = new Object();
        Object second = new Object();

        Thread one = new Thread(() -> hold(first, second));
        Thread two = new Thread(() -> hold(second, first));
        one.setDaemon(true);
        two.setDaemon(true);
        one.start();
        two.start();
        one.join(500);
        two.join(500);

        System.out.println("t1 still waiting : " + one.isAlive());
        System.out.println("t2 still waiting : " + two.isAlive());
        System.out.println();
        System.out.println("two locks, taken in two orders, and no way out: neither");
        System.out.println("thread can release the one the other is waiting for.");

        System.out.println();
        Object left = new Object();
        Object right = new Object();
        Thread three = new Thread(() -> hold(left, right));
        Thread four = new Thread(() -> hold(left, right));
        three.start();
        four.start();
        three.join(5_000);
        four.join(5_000);
        System.out.println("same locks, one order, both finished : "
                + (!three.isAlive() && !four.isAlive()));
        System.out.println();
        System.out.println("the fix is an order, not a timeout: if every thread takes the");
        System.out.println("locks in the same sequence, a cycle cannot form");

        System.out.println();
        ReentrantLock a = new ReentrantLock();
        ReentrantLock b = new ReentrantLock();
        b.lock();
        Thread patient = new Thread(() -> {
            a.lock();
            try {
                boolean got = false;
                try {
                    got = b.tryLock(100, TimeUnit.MILLISECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("tryLock got the second lock : " + got);
            } finally {
                a.unlock();
            }
        });
        patient.start();
        patient.join(5_000);
        b.unlock();
        System.out.println("finished instead of hanging : " + !patient.isAlive());
    }

    static void hold(Object a, Object b) {
        synchronized (a) {
            Nap.millis(200);
            synchronized (b) {
                Nap.millis(10);
            }
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Deadlock.java
java -cp out Deadlock
