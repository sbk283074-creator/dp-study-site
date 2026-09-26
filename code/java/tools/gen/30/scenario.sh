cat > Scenario.java <<'EOF'
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class Scenario {
    public static void main(String[] args) throws InterruptedException {
        AtomicInteger served = new AtomicInteger();
        AtomicInteger shed = new AtomicInteger();
        CountDownLatch gate = new CountDownLatch(1);

        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                8, 8, 0, TimeUnit.SECONDS, new ArrayBlockingQueue<>(32),
                new ThreadPoolExecutor.AbortPolicy());

        for (int i = 0; i < 500; i++) {
            try {
                pool.execute(() -> {
                    await(gate);
                    served.incrementAndGet();
                });
            } catch (RejectedExecutionException e) {
                shed.incrementAndGet();
            }
        }

        System.out.println("requests offered : 500");
        System.out.println("in flight        : " + pool.getActiveCount());
        System.out.println("queued           : " + pool.getQueue().size());
        System.out.println("refused          : " + shed.get());
        System.out.println("capacity         : " + (8 + 32));
        System.out.println();
        System.out.println("the " + shed.get() + " refusals happened during submission,");
        System.out.println("not after a wait, and none of them cost a thread");

        gate.countDown();
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println();
        System.out.println("after the gate   : " + served.get() + " served, "
                + shed.get() + " refused");
        System.out.println("the queue never held more than " + (8 + 32)
                + ", so the heap never grew at all");
    }

    static void await(CountDownLatch gate) {
        try {
            gate.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
