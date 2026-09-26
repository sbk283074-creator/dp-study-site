cat > Sol1.java <<'JAVA'
import java.sql.SQLException;

public class Sol1 {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);
        store.seed("bob", 0);

        try (Conn c = store.connect("main")) {
            c.begin();
            c.move("alice", "bob", 40);
            System.out.println("inside          : alice " + c.balance("alice")
                    + ", bob " + c.balance("bob"));
            c.rollback();
            System.out.println("after rollback  : alice " + c.balance("alice")
                    + ", bob " + c.balance("bob"));
            System.out.println("in transaction  : " + c.inTransaction());
            System.out.println();
            System.out.println("rollback discards the pending writes, so the committed state");
            System.out.println("is exactly what it was before begin()");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
