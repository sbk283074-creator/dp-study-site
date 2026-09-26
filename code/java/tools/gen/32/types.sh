cat > Types.java <<'JAVA'
import java.sql.SQLException;

public class Types {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, title TEXT, stars INTEGER)");
            db.update("INSERT INTO notes (id, title, stars) VALUES (?, ?, ?)", 1, "first", 5);
            db.update("INSERT INTO notes (id, title, stars) VALUES (?, ?, ?)", 2, null, null);

            try {
                db.query("SELECT id, title, stars FROM notes ORDER");
            } catch (SQLException e) {
                System.out.println("a typo is a SQLException, not a compile error:");
                System.out.println("  " + e.getMessage());
            }

            try (Rows rows = db.query("SELECT id, title, stars FROM notes")) {
                System.out.println();
                System.out.println("columns      : " + rows.columns());
                while (rows.next()) {
                    String title = rows.getString(2);
                    System.out.println("  id " + rows.getInt(1)
                            + " | title " + (title == null ? "null" : title)
                            + " | stars " + rows.getInt(3));
                }
            }

            try (Rows rows = db.query("SELECT id FROM notes")) {
                rows.next();
                try {
                    rows.get(9);
                } catch (SQLException e) {
                    System.out.println();
                    System.out.println("column 9     : " + e.getMessage());
                }
            }

            Rows rows = db.query("SELECT id FROM notes");
            rows.next();
            rows.close();
            try {
                rows.next();
            } catch (SQLException e) {
                System.out.println("after close  : " + e.getMessage());
            }
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Types.java
java -cp out Types
