cat > Flaky.java <<'JAVA'
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

public class Flaky {
    public static void main(String[] args) throws Exception {
        AtomicReference<String> answer = new AtomicReference<>("none");
        CountDownLatch done = new CountDownLatch(1);

        Thread worker = new Thread(() -> {
            answer.set("finished");
            done.countDown();
        });
        worker.start();

        boolean byLatch = done.await(5, TimeUnit.SECONDS);
        System.out.println("waited on a latch : " + byLatch + ", answer " + answer.get());

        Thread.sleep(50);
        System.out.println("waited on a sleep : true, answer " + answer.get());
        System.out.println();

        System.out.println("the sleep passes here and would pass on your machine, and that is");
        System.out.println("exactly the problem: it passes whether or not the work finished.");
        System.out.println("A latch fails when the work is slow, which is the only behaviour");
        System.out.println("that makes a slow machine visible instead of merely unlucky");

        System.out.println();
        AtomicReference<String> second = new AtomicReference<>("none");
        CountDownLatch later = new CountDownLatch(1);
        Thread slow = new Thread(() -> {
            try {
                Thread.sleep(300);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            second.set("finished");
            later.countDown();
        });
        slow.start();
        boolean tooShort = later.await(50, TimeUnit.MILLISECONDS);
        System.out.println("a 50 ms wait for 300 ms of work : " + tooShort);
        later.await(5, TimeUnit.SECONDS);
        System.out.println("and after waiting properly      : " + second.get());
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Flaky.java
java -cp out Flaky
