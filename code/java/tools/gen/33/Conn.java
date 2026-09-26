import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * One connection: it sees its own uncommitted writes, and nothing else does until
 * commit(). That single property is what "read committed" isolation means.
 */
public final class Conn implements AutoCloseable {

    private final Store store;
    private final String name;
    private Map<String, Long> pending;
    private boolean closed;

    Conn(Store store, String name) {
        this.store = store;
        this.name = name;
    }

    public String name() {
        return name;
    }

    public void begin() throws SQLException {
        requireOpen();
        if (pending != null) {
            throw new SQLException("a transaction is already open on " + name);
        }
        pending = new LinkedHashMap<>();
    }

    public void commit() throws SQLException {
        requireOpen();
        if (pending == null) {
            throw new SQLException("no transaction is open on " + name);
        }
        store.committed.putAll(pending);
        pending = null;
    }

    public void rollback() throws SQLException {
        requireOpen();
        if (pending == null) {
            throw new SQLException("no transaction is open on " + name);
        }
        pending = null;
    }

    public boolean inTransaction() {
        return pending != null;
    }

    public long balance(String account) throws SQLException {
        requireOpen();
        Long value = null;
        if (pending != null && pending.containsKey(account)) {
            value = pending.get(account);
        } else {
            value = store.committed.get(account);
        }
        if (value == null) {
            throw new SQLException("no such account: " + account);
        }
        return value;
    }

    /** Two writes that must both happen, or neither. */
    public void move(String from, String to, long amount) throws SQLException {
        requireOpen();
        long source = balance(from);
        if (source < amount) {
            throw new SQLException("insufficient funds in " + from);
        }
        write(from, source - amount);
        write(to, balance(to) + amount);
    }

    public void write(String account, long value) throws SQLException {
        requireOpen();
        if (!store.committed.containsKey(account)) {
            throw new SQLException("no such account: " + account);
        }
        if (pending != null) {
            pending.put(account, value);
        } else {
            store.committed.put(account, value);
        }
    }

    public boolean isClosed() {
        return closed;
    }

    @Override
    public void close() {
        pending = null;
        closed = true;
    }

    private void requireOpen() throws SQLException {
        if (closed) {
            throw new SQLException("this connection is closed");
        }
    }
}
