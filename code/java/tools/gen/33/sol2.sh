cat > Sol2.java <<'JAVA'
import java.sql.SQLException;

public class Sol2 {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);

        try (Conn writer = store.connect("writer"); Conn reader = store.connect("reader")) {
            writer.begin();
            writer.write("alice", 5);
            System.out.println("writer sees     : " + writer.balance("alice"));
            System.out.println("reader sees     : " + reader.balance("alice"));
            writer.rollback();
            System.out.println("reader, rolled  : " + reader.balance("alice"));
            System.out.println();
            System.out.println("a dirty read is reading the 5 before it was committed. Read");
            System.out.println("committed forbids it, and it is the default in every database");
            System.out.println("you are likely to use -- Postgres, MySQL and SQL Server alike");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
