cat > Scenario.java <<'JAVA'
import java.sql.SQLException;

public class Scenario {
    public static void main(String[] args) throws SQLException {
        int rows = 10;

        System.out.println("--- a batch job that borrows and never returns ---");
        try (Pool pool = new Pool(4, 100)) {
            int used = 0;
            int refused = 0;
            for (int i = 0; i < rows; i++) {
                try {
                    pool.borrow();
                    used++;
                } catch (SQLException e) {
                    refused++;
                }
            }
            System.out.println("  rows          : " + rows);
            System.out.println("  processed     : " + used);
            System.out.println("  refused       : " + refused);
        }

        System.out.println();
        System.out.println("--- the same job, returning each one ---");
        try (Pool pool = new Pool(4, 100)) {
            int used = 0;
            int refused = 0;
            java.util.Set<Integer> tickets = new java.util.TreeSet<>();
            for (int i = 0; i < rows; i++) {
                try (Pool.Ticket ticket = pool.borrow()) {
                    tickets.add(ticket.id());
                    used++;
                } catch (SQLException e) {
                    refused++;
                }
            }
            System.out.println("  rows          : " + rows);
            System.out.println("  processed     : " + used);
            System.out.println("  refused       : " + refused);
            System.out.println("  tickets used  : " + tickets);
            System.out.println("  pool size     : " + pool.size());
            System.out.println();
            System.out.println("four connections processed ten rows, because each one went");
            System.out.println("back before the next was needed. The leak was not a missing");
            System.out.println("close() on a socket, it was a missing close() on a ticket");
        }
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
