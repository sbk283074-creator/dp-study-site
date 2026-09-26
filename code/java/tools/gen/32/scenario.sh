cat > Scenario.java <<'JAVA'
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class Scenario {
    public static void main(String[] args) throws SQLException {
        try (Db db = Db.open()) {
            db.execute("CREATE TABLE users (id INTEGER, email TEXT, plan TEXT)");
            seed(db);

            System.out.println("--- an endpoint that takes an email ---");
            System.out.println("  found      : " + findByEmail(db, "bob@example.com"));
            System.out.println("  not found  : " + findByEmail(db, "nobody@example.com"));
            System.out.println("  hostile    : " + findByEmail(db, "' OR '1'='1"));
            System.out.println();

            System.out.println("--- the same lookup, concatenated ---");
            String hostile = "' OR '1'='1";
            String unsafe = "SELECT email FROM users WHERE email = '" + hostile + "'";
            System.out.println("  sql        : " + unsafe);
            try {
                db.query(unsafe);
            } catch (SQLException e) {
                System.out.println("  result     : " + e.getMessage());
            }
            System.out.println();
            System.out.println("the value never became syntax, because it was never parsed");
            System.out.println("as SQL -- it arrived as data, in its own channel");
        }
    }

    static void seed(Db db) throws SQLException {
        db.update("INSERT INTO users (id, email, plan) VALUES (?, ?, ?)", 1, "bob@example.com", "pro");
        db.update("INSERT INTO users (id, email, plan) VALUES (?, ?, ?)", 2, "ada@example.com", "free");
    }

    static List<String> findByEmail(Db db, String email) throws SQLException {
        List<String> out = new ArrayList<>();
        try (Rows rows = db.query("SELECT email FROM users WHERE email = ?", email)) {
            while (rows.next()) {
                out.add(rows.getString(1));
            }
        }
        return out;
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
