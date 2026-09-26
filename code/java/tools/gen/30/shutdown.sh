cat > Stopping.java <<'EOF'
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Stopping {
    public static void main(String[] args) throws InterruptedException {
        Work.reset();
        ExecutorService pool = Executors.newFixedThreadPool(2);
        for (int i = 0; i < 20; i++) {
            pool.execute(() -> {
                Work.sleep(300);
                Work.finish();
            });
        }

        pool.shutdown();
        System.out.println("shutdown() lets queued work finish; it accepts nothing new");
        boolean quick = pool.awaitTermination(50, TimeUnit.MILLISECONDS);
        System.out.println("terminated within 50 ms : " + quick);
        boolean patient = pool.awaitTermination(30, TimeUnit.SECONDS);
        System.out.println("terminated eventually  : " + patient);
        System.out.println("tasks that ran         : " + Work.done());

        System.out.println();
        Work.reset();
        ExecutorService hard = Executors.newFixedThreadPool(2);
        for (int i = 0; i < 20; i++) {
            hard.execute(() -> {
                Work.sleep(5_000);
                Work.finish();
            });
        }
        Work.sleep(100);
        List<Runnable> neverStarted = hard.shutdownNow();
        System.out.println("shutdownNow() returned " + neverStarted.size()
                + " task(s) that never started");
        boolean stopped = hard.awaitTermination(10, TimeUnit.SECONDS);
        System.out.println("terminated             : " + stopped);
        System.out.println("tasks that finished    : " + Work.done());
        System.out.println();
        System.out.println("shutdownNow() interrupts the workers; a task that catches");
        System.out.println("InterruptedException and keeps going will not stop");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Stopping.java
java -cp out Stopping
