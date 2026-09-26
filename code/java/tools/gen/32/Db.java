import java.sql.SQLException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * A very small SQL engine: CREATE TABLE, INSERT, SELECT, UPDATE, DELETE and
 * COUNT(*). It throws the real java.sql.SQLException, so the exception handling
 * in this chapter is the exception handling you would write against a driver.
 */
public final class Db implements AutoCloseable {

    public static final class Table {
        final List<String> columns = new ArrayList<>();
        final List<Object[]> rows = new ArrayList<>();
    }

    private final Map<String, Table> tables = new LinkedHashMap<>();
    private boolean closed;

    private Db() {
    }

    public static Db open() {
        return new Db();
    }

    public void execute(String sql) throws SQLException {
        requireOpen();
        String text = normalise(sql);
        if (text.startsWith("CREATE TABLE ")) {
            String rest = text.substring("CREATE TABLE ".length());
            int open = rest.indexOf('(');
            String name = rest.substring(0, open).trim();
            String body = rest.substring(open + 1, rest.lastIndexOf(')'));
            Table table = new Table();
            for (String part : body.split(",")) {
                table.columns.add(part.trim().split("\\s+")[0].toLowerCase(Locale.ROOT));
            }
            tables.put(name.toLowerCase(Locale.ROOT), table);
            return;
        }
        throw new SQLException("unsupported statement: " + sql);
    }

    public int update(String sql, Object... params) throws SQLException {
        requireOpen();
        String text = normalise(sql);
        int used = 0;

        if (text.startsWith("INSERT INTO ")) {
            String rest = text.substring("INSERT INTO ".length());
            int open = rest.indexOf('(');
            int close = rest.indexOf(')');
            Table table = require(rest.substring(0, open).trim());
            List<String> columns = split(rest.substring(open + 1, close));
            String values = rest.substring(rest.indexOf("VALUES ") + 7).trim();
            List<String> slots = split(values.substring(1, values.lastIndexOf(')')));

            Object[] row = new Object[table.columns.size()];
            for (int i = 0; i < columns.size(); i++) {
                int at = table.columns.indexOf(columns.get(i).toLowerCase(Locale.ROOT));
                if (at < 0) {
                    throw new SQLException("no such column: " + columns.get(i));
                }
                if (slots.get(i).equals("?")) {
                    row[at] = params[used++];
                } else {
                    row[at] = literal(slots.get(i));
                }
            }
            table.rows.add(row);
            return 1;
        }

        String where = null;
        int at = text.indexOf(" WHERE ");
        if (at >= 0) {
            where = text.substring(at + 7);
            text = text.substring(0, at);
        }
        Object[] bound = bind(where, params, used);

        if (text.startsWith("UPDATE ")) {
            String rest = text.substring("UPDATE ".length());
            int setAt = rest.indexOf(" SET ");
            Table table = require(rest.substring(0, setAt).trim());
            String assignment = rest.substring(setAt + 5).trim();
            String[] parts = assignment.split("=", 2);
            int column = table.columns.indexOf(parts[0].trim().toLowerCase(Locale.ROOT));
            if (column < 0) {
                throw new SQLException("no such column: " + parts[0].trim());
            }
            int changed = 0;
            for (Object[] row : table.rows) {
                if (matches(table, where, row, bound)) {
                    row[column] = bound[0];
                    changed++;
                }
            }
            return changed;
        }

        if (text.startsWith("DELETE FROM ")) {
            Table table = require(text.substring("DELETE FROM ".length()).trim());
            List<Object[]> keep = new ArrayList<>();
            int removed = 0;
            for (Object[] row : table.rows) {
                if (matches(table, where, row, bound)) {
                    removed++;
                } else {
                    keep.add(row);
                }
            }
            table.rows.clear();
            table.rows.addAll(keep);
            return removed;
        }

        throw new SQLException("unsupported statement: " + sql);
    }

    public Rows query(String sql, Object... params) throws SQLException {
        requireOpen();
        String text = normalise(sql);
        if (!text.startsWith("SELECT ")) {
            throw new SQLException("not a query: " + sql);
        }
        String rest = text.substring("SELECT ".length());
        int from = rest.indexOf(" FROM ");
        String projection = rest.substring(0, from).trim();
        rest = rest.substring(from + 6).trim();

        String where = null;
        int at = rest.indexOf(" WHERE ");
        if (at >= 0) {
            where = rest.substring(at + 7);
            rest = rest.substring(0, at).trim();
        }
        Table table = require(rest.trim());
        Object[] bound = bind(where, params, 0);

        List<Object[]> found = new ArrayList<>();
        for (Object[] row : table.rows) {
            if (matches(table, where, row, bound)) {
                found.add(row);
            }
        }

        List<String> labels = new ArrayList<>();
        List<Object[]> out = new ArrayList<>();
        if (projection.equals("COUNT(*)")) {
            labels.add("count");
            out.add(new Object[]{found.size()});
            return new Rows(labels, out);
        }
        if (projection.equals("*")) {
            labels.addAll(table.columns);
            out.addAll(found);
            return new Rows(labels, out);
        }
        List<String> wanted = split(projection);
        for (String name : wanted) {
            labels.add(name.toLowerCase(Locale.ROOT));
        }
        for (Object[] row : found) {
            Object[] picked = new Object[wanted.size()];
            for (int i = 0; i < wanted.size(); i++) {
                int index = table.columns.indexOf(wanted.get(i).toLowerCase(Locale.ROOT));
                if (index < 0) {
                    throw new SQLException("no such column: " + wanted.get(i));
                }
                picked[i] = row[index];
            }
            out.add(picked);
        }
        return new Rows(labels, out);
    }

    public int tables() {
        return tables.size();
    }

    public boolean isClosed() {
        return closed;
    }

    @Override
    public void close() {
        closed = true;
    }

    private Table require(String name) throws SQLException {
        Table table = tables.get(name.toLowerCase(Locale.ROOT));
        if (table == null) {
            throw new SQLException("no such table: " + name);
        }
        return table;
    }

    private static Object[] bind(String where, Object[] params, int from) throws SQLException {
        if (where == null) {
            return new Object[0];
        }
        String[] parts = where.split("=", 2);
        if (parts.length != 2) {
            throw new SQLException("only `column = ?` is supported, got: " + where);
        }
        String right = parts[1].trim();
        return new Object[]{right.equals("?") ? params[from] : literal(right)};
    }

    private static boolean matches(Table table, String where, Object[] row, Object[] bound)
            throws SQLException {
        if (where == null) {
            return true;
        }
        String column = where.split("=", 2)[0].trim().toLowerCase(Locale.ROOT);
        int index = table.columns.indexOf(column);
        if (index < 0) {
            throw new SQLException("no such column: " + column);
        }
        Object left = row[index];
        Object right = bound[0];
        return left == null ? right == null : left.equals(right);
    }

    private static Object literal(String token) {
        String text = token.trim();
        if (text.startsWith("'") && text.endsWith("'")) {
            return text.substring(1, text.length() - 1);
        }
        if (text.matches("-?\\d+")) {
            return Long.parseLong(text);
        }
        return text;
    }

    private static List<String> split(String list) {
        List<String> out = new ArrayList<>();
        for (String part : list.split(",")) {
            out.add(part.trim());
        }
        return out;
    }

    private static String normalise(String sql) {
        return sql.trim().replaceAll("\\s+", " ");
    }

    private void requireOpen() throws SQLException {
        if (closed) {
            throw new SQLException("this connection is closed");
        }
    }
}
