import java.sql.SQLException;

public class DbDemo {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE people (id INTEGER, name TEXT, age INTEGER)");

            db.update("INSERT INTO people (id, name, age) VALUES (?, ?, ?)", 1, "alice", 30);
            db.update("INSERT INTO people (id, name, age) VALUES (?, ?, ?)", 2, "bob", 41);
            db.update("INSERT INTO people (id, name, age) VALUES (?, ?, ?)", 3, "cara", 27);

            System.out.println("--- select * ---");
            try (Rows rows = db.query("SELECT * FROM people")) {
                System.out.println("columns : " + rows.columns());
                while (rows.next()) {
                    System.out.println("  " + rows.getInt(1) + " | " + rows.getString(2)
                            + " | " + rows.getInt(3));
                }
            }

            System.out.println();
            System.out.println("--- a projection and a placeholder ---");
            try (Rows rows = db.query("SELECT name, age FROM people WHERE id = ?", 2)) {
                while (rows.next()) {
                    System.out.println("  " + rows.getString(1) + " is " + rows.getInt(2));
                }
            }

            System.out.println();
            System.out.println("--- count(*), update, delete ---");
            try (Rows rows = db.query("SELECT COUNT(*) FROM people")) {
                rows.next();
                System.out.println("  before      : " + rows.getInt(1));
            }
            System.out.println("  updated     : "
                    + db.update("UPDATE people SET age = ? WHERE name = ?", 42, "bob"));
            try (Rows rows = db.query("SELECT name, age FROM people WHERE name = 'bob'")) {
                while (rows.next()) {
                    System.out.println("  bob is now  : " + rows.getInt(2));
                }
            }
            System.out.println("  deleted     : "
                    + db.update("DELETE FROM people WHERE id = ?", 3));
            try (Rows rows = db.query("SELECT COUNT(*) FROM people")) {
                rows.next();
                System.out.println("  after       : " + rows.getInt(1));
            }
        }
    }
}
