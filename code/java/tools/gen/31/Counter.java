import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.LongAdder;

/** One counter four ways, so a chapter can measure what each one actually guarantees. */
public final class Counter {

    private int plain;
    private final AtomicInteger atomic = new AtomicInteger();
    private final LongAdder adder = new LongAdder();

    public Counter(int start) {
        plain = start;
        atomic.set(start);
    }

    public int plain() {
        return plain;
    }

    public void setPlain(int value) {
        plain = value;
    }

    public synchronized void bumpLocked() {
        plain = plain + 1;
    }

    public AtomicInteger atomic() {
        return atomic;
    }

    public LongAdder adder() {
        return adder;
    }
}
