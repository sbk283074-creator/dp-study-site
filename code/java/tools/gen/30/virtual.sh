cat > Virtual.java <<'EOF'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Virtual {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 1_000;
        AtomicInteger virtual = new AtomicInteger();

        long start = System.nanoTime();
        ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
        for (int i = 0; i < tasks; i++) {
            pool.execute(() -> {
                if (Thread.currentThread().isVirtual()) {
                    virtual.incrementAndGet();
                }
                Work.sleep(20);
            });
        }
        pool.shutdown();
        pool.awaitTermination(60, TimeUnit.SECONDS);
        long millis = (System.nanoTime() - start) / 1_000_000L;

        System.out.println("tasks submitted   : " + tasks);
        System.out.println("ran on a virtual  : " + virtual.get());
        System.out.println("wall under 1s     : " + (millis < 1000));
        System.out.println();
        System.out.println("a virtual thread is a task, not a resource: one per request");
        System.out.println("is affordable because none of them owns an OS thread");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Virtual.java
java -cp out Virtual
