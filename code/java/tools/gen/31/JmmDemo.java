import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

public class JmmDemo {
    public static void main(String[] args) throws Exception {
        System.out.println("two threads, one increment each, starting from 5");
        System.out.println();
        System.out.println("  plain int, read then write   : " + racy() + "   (correct would be 7)");
        System.out.println("  guarded by synchronized      : " + locked() + "   (correct would be 7)");
        System.out.println("  through AtomicInteger        : " + atomic() + "   (correct would be 7)");
        System.out.println();
        System.out.println("four threads, 50_000 increments each, starting from 0");
        System.out.println();
        System.out.println("  AtomicInteger : " + contended(false) + "   (correct would be 200000)");
        System.out.println("  LongAdder     : " + contended(true) + "   (correct would be 200000)");
    }

    /** Both threads read 5, then both write 6. The barrier only makes it reproducible. */
    static int racy() throws Exception {
        Counter counter = new Counter(5);
        CyclicBarrier bothRead = new CyclicBarrier(2);
        CyclicBarrier bothWrote = new CyclicBarrier(3);

        Runnable task = () -> {
            int seen = counter.plain();
            await(bothRead);
            Nap.millis(50);
            counter.setPlain(seen + 1);
            await(bothWrote);
        };

        Thread a = new Thread(task);
        Thread b = new Thread(task);
        a.start();
        b.start();
        await(bothWrote);
        return counter.plain();
    }

    static int locked() throws Exception {
        Counter counter = new Counter(5);
        CyclicBarrier start = new CyclicBarrier(2);
        CyclicBarrier done = new CyclicBarrier(3);

        Runnable task = () -> {
            await(start);
            counter.bumpLocked();
            await(done);
        };

        Thread a = new Thread(task);
        Thread b = new Thread(task);
        a.start();
        b.start();
        await(done);
        return counter.plain();
    }

    static int atomic() {
        Counter counter = new Counter(5);
        counter.atomic().incrementAndGet();
        counter.atomic().incrementAndGet();
        return counter.atomic().get();
    }

    static long contended(boolean useAdder) throws InterruptedException {
        Counter counter = new Counter(0);
        int threads = 4;
        int per = 50_000;
        Thread[] pool = new Thread[threads];

        for (int i = 0; i < threads; i++) {
            pool[i] = new Thread(() -> {
                for (int n = 0; n < per; n++) {
                    if (useAdder) {
                        counter.adder().increment();
                    } else {
                        counter.atomic().incrementAndGet();
                    }
                }
            });
        }
        for (Thread t : pool) {
            t.start();
        }
        for (Thread t : pool) {
            t.join();
        }
        return useAdder ? counter.adder().sum() : counter.atomic().get();
    }

    static void await(CyclicBarrier barrier) {
        try {
            barrier.await();
        } catch (InterruptedException | BrokenBarrierException e) {
            throw new IllegalStateException(e);
        }
    }
}
