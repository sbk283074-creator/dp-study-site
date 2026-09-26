cat > Sol3.java <<'JAVA'
import java.sql.SQLException;

public class Sol3 {
    public static void main(String[] args) throws SQLException {
        try (Pool pool = new Pool(3, 100)) {
            pool.borrow();
            pool.borrow();
            pool.borrow();
            System.out.println("size            : " + pool.size());
            System.out.println("in use          : " + pool.inUse());
            try {
                pool.borrow();
            } catch (SQLException e) {
                System.out.println("the fourth      : " + e.getMessage());
            }
            System.out.println();
            System.out.println("a bounded wait turns \"the pool is exhausted\" into an error");
            System.out.println("the caller can catch, log and retry -- instead of a thread");
            System.out.println("that blocks forever holding a request slot it cannot fill");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
