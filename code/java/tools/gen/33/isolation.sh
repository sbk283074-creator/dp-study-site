cat > Isolation.java <<'JAVA'
import java.sql.SQLException;

public class Isolation {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);

        try (Conn writer = store.connect("writer"); Conn reader = store.connect("reader")) {
            writer.write("alice", 10);
            System.out.println("autocommit      : " + reader.balance("alice"));

            writer.begin();
            writer.write("alice", 20);
            System.out.println("uncommitted     : " + reader.balance("alice"));
            System.out.println("writer's view   : " + writer.balance("alice"));
            writer.commit();
            System.out.println("committed       : " + reader.balance("alice"));

            writer.begin();
            writer.write("alice", 30);
            writer.rollback();
            System.out.println("rolled back     : " + reader.balance("alice"));
            System.out.println();
            System.out.println("without begin(), every statement is its own transaction and");
            System.out.println("commits immediately -- which is why a two-statement update");
            System.out.println("needs setAutoCommit(false) before it is safe");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Isolation.java
java -cp out Isolation
