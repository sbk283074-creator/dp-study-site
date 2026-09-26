cat > Pooled.java <<'JAVA'
import java.sql.SQLException;

public class Pooled {
    public static void main(String[] args) throws SQLException {
        try (Pool pool = new Pool(2, 100)) {
            Pool.Ticket one = pool.borrow();
            Pool.Ticket two = pool.borrow();
            System.out.println("borrowed        : " + one.id() + ", " + two.id());
            System.out.println("pool size       : " + pool.size());
            System.out.println("in use          : " + pool.inUse());
            System.out.println("idle            : " + pool.idle());

            try {
                pool.borrow();
            } catch (SQLException e) {
                System.out.println("a third borrow  : " + e.getMessage());
            }

            one.close();
            System.out.println("after returning : in use " + pool.inUse()
                    + ", idle " + pool.idle());

            Pool.Ticket again = pool.borrow();
            System.out.println("borrowed again  : " + again.id());
            System.out.println("pool size       : " + pool.size());
            System.out.println();
            System.out.println("the pool never grew past two, because two is its maximum. The");
            System.out.println("third caller waited, gave up, and got an error it can act on");
            System.out.println("instead of a connection the database will not give out");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Pooled.java
java -cp out Pooled
