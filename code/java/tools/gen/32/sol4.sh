cat > Sol4.java <<'JAVA'
import java.sql.SQLException;

public class Sol4 {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE notes (id INTEGER, body TEXT, stars INTEGER)");
            db.update("INSERT INTO notes (id, body, stars) VALUES (?, ?, ?)", 1, "a", 5);
            db.update("INSERT INTO notes (id, body, stars) VALUES (?, ?, ?)", 2, "b", 3);
            db.update("INSERT INTO notes (id, body, stars) VALUES (?, ?, ?)", 3, "c", 4);

            int total = 0;
            int seen = 0;
            try (Rows rows = db.query("SELECT body, stars FROM notes")) {
                while (rows.next()) {
                    total += rows.getInt(2);
                    seen++;
                }
            }
            System.out.println("rows         : " + seen);
            System.out.println("total stars  : " + total);
            System.out.println();
            System.out.println("the cursor starts before the first row, so a while(next())");
            System.out.println("loop visits each row exactly once and then stops");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
