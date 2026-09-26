cat > Sol4.java <<'JAVA'
import java.sql.SQLException;

public class Sol4 {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);
        store.seed("bob", 100);

        try (Conn a = store.connect("A"); Conn b = store.connect("B")) {
            a.begin();
            b.begin();
            a.write("alice", 90);
            b.write("bob", 90);
            System.out.println("A holds alice, B holds bob, both uncommitted");
            a.commit();
            b.commit();
            System.out.println("after both commit : alice " + a.balance("alice")
                    + ", bob " + b.balance("bob"));
            System.out.println();
            System.out.println("two connections can hold open transactions at once as long as");
            System.out.println("they touch different rows. A deadlock needs both to want what");
            System.out.println("the other one has already locked, and then a database picks a");
            System.out.println("victim and rolls it back rather than waiting forever");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
