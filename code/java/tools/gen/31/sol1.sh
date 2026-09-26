cat > Sol1.java <<'JAVA'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Sol1 {
    public static void main(String[] args) throws InterruptedException {
        int threads = 4;
        int per = 20_000;
        AtomicInteger hits = new AtomicInteger();
        ExecutorService pool = Executors.newFixedThreadPool(threads);

        for (int i = 0; i < threads; i++) {
            pool.execute(() -> {
                for (int n = 0; n < per; n++) {
                    hits.incrementAndGet();
                }
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("threads          : " + threads);
        System.out.println("increments each  : " + per);
        System.out.println("expected         : " + (threads * per));
        System.out.println("counted          : " + hits.get());
        System.out.println();
        System.out.println("incrementAndGet is a single atomic operation, so no increment");
        System.out.println("can be lost no matter how the threads interleave");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
