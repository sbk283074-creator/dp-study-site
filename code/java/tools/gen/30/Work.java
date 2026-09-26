import java.util.LinkedHashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

/** A unit of work that is slow on purpose, so that a pool has something to queue. */
public final class Work {

    private static final Set<String> THREADS = new LinkedHashSet<>();
    private static final AtomicInteger DONE = new AtomicInteger();

    private Work() {
    }

    /** Sleeps, restoring the interrupt flag rather than swallowing it. */
    public static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /** Records which thread ran this task, so a chapter can count them. */
    public static void finish() {
        synchronized (THREADS) {
            THREADS.add(Thread.currentThread().getName());
        }
        DONE.incrementAndGet();
    }

    public static int distinctThreads() {
        synchronized (THREADS) {
            return THREADS.size();
        }
    }

    public static String[] threadNames() {
        synchronized (THREADS) {
            return THREADS.toArray(new String[0]);
        }
    }

    public static int done() {
        return DONE.get();
    }

    public static void reset() {
        synchronized (THREADS) {
            THREADS.clear();
        }
        DONE.set(0);
    }
}
