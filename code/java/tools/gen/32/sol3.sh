cat > Sol3.java <<'JAVA'
import java.sql.SQLException;

public class Sol3 {
    public static void main(String[] args) throws SQLException {
        Db db = Db.open();
        db.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
        db.close();

        try {
            db.query("SELECT id FROM notes");
        } catch (SQLException e) {
            System.out.println("after close  : " + e.getMessage());
        }

        try (Db second = Db.open()) {
            second.execute("CREATE TABLE notes (id INTEGER, body TEXT)");
            try {
                second.execute("CREATE TABLE notes (id INTEGER)");
            } catch (SQLException e) {
                System.out.println("duplicate    : " + e.getMessage());
            }
        }
        System.out.println();
        System.out.println("a SQLException carries a message, a SQLState and a vendor code,");
        System.out.println("which is why logging only its class name is never enough");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
