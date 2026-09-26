cat > Drain.java <<'JAVA'
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Drain {
    public static void main(String[] args) throws InterruptedException {
        AtomicInteger finished = new AtomicInteger();
        CountDownLatch inFlight = new CountDownLatch(3);
        ExecutorService pool = Executors.newFixedThreadPool(4);

        for (int i = 0; i < 3; i++) {
            pool.execute(() -> {
                try {
                    Thread.sleep(200);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                finished.incrementAndGet();
                inFlight.countDown();
            });
        }

        System.out.println("shutting down with 3 requests still running");
        pool.shutdown();
        boolean drained = pool.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("  finished before exit : " + finished.get());
        System.out.println("  drained              : " + drained);
        System.out.println();
        System.out.println("a graceful stop is two things in order: stop accepting new work,");
        System.out.println("then wait for the work already accepted. shutdown() does the");
        System.out.println("first and awaitTermination the second, and skipping either one");
        System.out.println("means either a request that never started or one that was cut off");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Drain.java
java -cp out Drain
