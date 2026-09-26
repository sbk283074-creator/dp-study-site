cat > Injection.java <<'JAVA'
import java.sql.SQLException;

public class Injection {
    public static void main(String[] args) throws SQLException {
        String name = "bob'); DROP TABLE people; --";

        try (Db db = Db.open()) {
            db.execute("CREATE TABLE people (id INTEGER, name TEXT)");

            String unsafe = "INSERT INTO people (id, name) VALUES (1, '" + name + "')";
            System.out.println("concatenated : " + unsafe);
            try {
                db.update(unsafe);
            } catch (SQLException e) {
                System.out.println("the engine   : " + e.getMessage());
            }

            db.update("INSERT INTO people (id, name) VALUES (?, ?)", 1, name);
            try (Rows rows = db.query("SELECT name FROM people")) {
                rows.next();
                System.out.println("bound        : " + rows.getString(1));
            }
            System.out.println();
            System.out.println("a placeholder is parsed once and sent separately, so the");
            System.out.println("value can never become syntax. This engine has no DROP, so");
            System.out.println("it rejected the statement; a real database would have run it.");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Injection.java
java -cp out Injection
