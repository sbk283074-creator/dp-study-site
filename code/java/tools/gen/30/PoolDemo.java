import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class PoolDemo {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 12;
        int workers = 3;

        ExecutorService pool = Executors.newFixedThreadPool(workers);
        for (int i = 0; i < tasks; i++) {
            pool.execute(() -> {
                Work.sleep(10);
                Work.finish();
            });
        }
        pool.shutdown();
        boolean ended = pool.awaitTermination(5, TimeUnit.SECONDS);

        System.out.println("tasks submitted : " + tasks);
        System.out.println("workers in pool : " + workers);
        System.out.println("tasks finished  : " + Work.done());
        System.out.println("threads used    : " + Work.distinctThreads());
        System.out.println("terminated      : " + ended);
        System.out.println();
        System.out.println(tasks + " tasks over " + Work.distinctThreads()
                + " threads. A pool is a bound, not an accelerator:");
        System.out.println("it decides how many things happen at once, and everything");
        System.out.println("else waits in the queue.");
    }
}
