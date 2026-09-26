cat > Sol4.java <<'EOF'
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class Sol4 {
    public static void main(String[] args) throws InterruptedException {
        CountDownLatch started = new CountDownLatch(1);
        ExecutorService polite = Executors.newFixedThreadPool(1);
        polite.execute(() -> {
            started.countDown();
            while (!Thread.currentThread().isInterrupted()) {
                Thread.onSpinWait();
            }
        });
        started.await();
        Work.sleep(50);
        polite.shutdownNow();
        boolean politeStopped = polite.awaitTermination(5, TimeUnit.SECONDS);

        CountDownLatch going = new CountDownLatch(1);
        AtomicBoolean release = new AtomicBoolean(false);
        ExecutorService rude = Executors.newFixedThreadPool(1);
        rude.execute(() -> {
            going.countDown();
            while (!release.get()) {
                Thread.onSpinWait();
            }
        });
        going.await();
        Work.sleep(50);
        rude.shutdownNow();
        boolean rudeStopped = rude.awaitTermination(300, TimeUnit.MILLISECONDS);
        release.set(true);
        rude.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("a task that checks isInterrupted : terminated " + politeStopped);
        System.out.println("a task that ignores it           : terminated " + rudeStopped);
        System.out.println();
        System.out.println("shutdownNow() only interrupts. Interruption in Java is a");
        System.out.println("request, and a task that never looks will never honour it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
