cat > Sol1.java <<'JAVA'
import java.sql.SQLException;

public class Sol1 {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
            for (int i = 1; i <= 5; i++) {
                db.update("INSERT INTO notes (id, body) VALUES (?, ?)", i, "note " + i);
            }
            try (Rows rows = db.query("SELECT id, body FROM notes")) {
                System.out.println("rows         : " + rows.size());
                while (rows.next()) {
                    System.out.println("  " + rows.getInt(1) + " " + rows.getString(2));
                }
            }
            System.out.println();
            System.out.println("the loop is the whole idiom: next() moves the cursor and");
            System.out.println("returns false when there is nothing left to move it to");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
