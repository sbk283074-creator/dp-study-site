import java.sql.SQLException;
import java.util.List;

/**
 * Stands in for java.sql.ResultSet: one-based column numbers, a cursor that starts
 * before the first row, and typed getters. The shape is JDBC's on purpose -- the
 * JDK ships no driver, so this is the closest thing that can be verified here.
 */
public final class Rows implements AutoCloseable {

    private final List<String> labels;
    private final List<Object[]> data;
    private int cursor = -1;
    private boolean closed;

    Rows(List<String> labels, List<Object[]> data) {
        this.labels = labels;
        this.data = data;
    }

    public boolean next() throws SQLException {
        requireOpen();
        cursor++;
        return cursor < data.size();
    }

    public Object get(int column) throws SQLException {
        requireOpen();
        if (cursor < 0 || cursor >= data.size()) {
            throw new SQLException("no current row: call next() before reading");
        }
        int index = column - 1;
        if (index < 0 || index >= labels.size()) {
            throw new SQLException("no such column index: " + column);
        }
        return data.get(cursor)[index];
    }

    public String getString(int column) throws SQLException {
        Object value = get(column);
        return value == null ? null : value.toString();
    }

    public int getInt(int column) throws SQLException {
        Object value = get(column);
        if (value == null) {
            return 0;
        }
        if (value instanceof Number number) {
            return number.intValue();
        }
        throw new SQLException("column " + column + " is not numeric: " + value);
    }

    public int columns() {
        return labels.size();
    }

    public String label(int column) {
        return labels.get(column - 1);
    }

    public int size() {
        return data.size();
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
            throw new SQLException("this result set is closed");
        }
    }
}
