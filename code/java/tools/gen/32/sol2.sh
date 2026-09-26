cat > Sol2.java <<'JAVA'
import java.sql.SQLException;

public class Sol2 {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
            db.update("INSERT INTO notes (id, body) VALUES (?, ?)", 1, "keep");
            db.update("INSERT INTO notes (id, body) VALUES (?, ?)", 2, "drop me");

            System.out.println("deleted      : " + db.update("DELETE FROM notes WHERE id = ?", 2));
            try (Rows rows = db.query("SELECT COUNT(*) FROM notes")) {
                rows.next();
                System.out.println("remaining    : " + rows.getInt(1));
            }
            System.out.println();
            System.out.println("the count is 1 and not 0, because the WHERE matched one row");
            System.out.println("and not every row -- which is what a missing WHERE would do");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
