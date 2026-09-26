cat > Pooled.java <<'EOF'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Pooled {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 100;
        int workers = 4;
        Work.reset();

        long start = System.nanoTime();
        ExecutorService pool = Executors.newFixedThreadPool(workers);
        for (int i = 0; i < tasks; i++) {
            pool.execute(() -> {
                Work.sleep(20);
                Work.finish();
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);
        long millis = (System.nanoTime() - start) / 1_000_000L;

        System.out.println("tasks            : " + tasks);
        System.out.println("workers in pool  : " + workers);
        System.out.println("threads created  : " + Work.distinctThreads());
        System.out.println("tasks finished   : " + Work.done());
        System.out.println("wall >= 400 ms   : " + (millis >= 400));
        System.out.println();
        System.out.println("same " + tasks + " tasks, " + Work.distinctThreads()
                + " threads. The work did not get smaller; it got queued.");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Pooled.java
java -cp out Pooled
