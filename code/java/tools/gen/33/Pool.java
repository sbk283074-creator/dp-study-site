import java.sql.SQLException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * A bounded pool of connections. Borrowing is capped and waiting is bounded, so a
 * saturated pool fails fast instead of growing until the database refuses.
 */
public final class Pool implements AutoCloseable {

    public static final class Ticket implements AutoCloseable {
        private final int id;
        private final Pool owner;
        private boolean inUse = true;

        Ticket(int id, Pool owner) {
            this.id = id;
            this.owner = owner;
        }

        public int id() {
            return id;
        }

        @Override
        public void close() {
            owner.giveBack(this);
        }
    }

    private final Deque<Ticket> idle = new ArrayDeque<>();
    private final List<Ticket> all = new ArrayList<>();
    private final int max;
    private final long timeoutMillis;
    private boolean closed;

    public Pool(int max, long timeoutMillis) {
        this.max = max;
        this.timeoutMillis = timeoutMillis;
    }

    public Ticket borrow() throws SQLException {
        long deadline = System.currentTimeMillis() + timeoutMillis;
        while (true) {
            synchronized (this) {
                requireOpen();
                if (!idle.isEmpty()) {
                    Ticket reuse = idle.pop();
                    reuse.inUse = true;
                    return reuse;
                }
                if (all.size() < max) {
                    Ticket fresh = new Ticket(all.size() + 1, this);
                    all.add(fresh);
                    return fresh;
                }
            }
            if (System.currentTimeMillis() > deadline) {
                throw new SQLException("no connection available within " + timeoutMillis
                        + " ms (pool size " + max + ", in use " + inUse() + ")");
            }
            sleep(5);
        }
    }

    public synchronized void giveBack(Ticket ticket) {
        if (ticket == null || !ticket.inUse) {
            return;
        }
        ticket.inUse = false;
        idle.push(ticket);
    }

    public synchronized int idle() {
        return idle.size();
    }

    public synchronized int inUse() {
        int busy = 0;
        for (Ticket ticket : all) {
            if (ticket.inUse) {
                busy++;
            }
        }
        return busy;
    }

    public synchronized int size() {
        return all.size();
    }

    public boolean isClosed() {
        return closed;
    }

    @Override
    public void close() {
        closed = true;
    }

    private void requireOpen() throws SQLException {
        if (closed) {
            throw new SQLException("this pool is closed");
        }
    }

    private static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
