import java.sql.SQLException;

public class TxDemo {
    public static void main(String[] args) throws SQLException {
        Store store = new Store();
        store.seed("alice", 100);
        store.seed("bob", 50);

        System.out.println("--- a transfer to an account that does not exist ---");
        try (Conn c = store.connect("c1")) {
            System.out.println("  alice before : " + c.balance("alice"));
            try {
                c.move("alice", "ghost", 30);
            } catch (SQLException e) {
                System.out.println("  failed       : " + e.getMessage());
            }
            System.out.println("  alice after  : " + c.balance("alice"));
            System.out.println();
            System.out.println("  30 has vanished: the withdrawal happened and stuck, and the");
            System.out.println("  deposit never ran. There is no code path that puts it back.");
        }

        System.out.println();
        System.out.println("--- the same transfer inside a transaction ---");
        try (Conn c = store.connect("c2")) {
            c.begin();
            try {
                c.move("alice", "ghost", 30);
            } catch (SQLException e) {
                System.out.println("  failed       : " + e.getMessage());
            }
            c.rollback();
            System.out.println("  alice after  : " + c.balance("alice"));
            System.out.println();
            System.out.println("  the half that happened was undone, so the transfer became");
            System.out.println("  all-or-nothing -- which is the whole point of a transaction");
        }

        System.out.println();
        System.out.println("--- a real transfer, committed ---");
        try (Conn c = store.connect("c3")) {
            c.begin();
            c.move("alice", "bob", 30);
            System.out.println("  inside the transaction, alice : " + c.balance("alice"));
            c.commit();
            System.out.println("  after commit, alice           : " + c.balance("alice"));
            System.out.println("  after commit, bob             : " + c.balance("bob"));
        }

        System.out.println();
        System.out.println("--- what the other connection saw, moment by moment ---");
        Store shared = new Store();
        shared.seed("alice", 100);
        shared.seed("bob", 50);
        try (Conn a = shared.connect("A"); Conn b = shared.connect("B")) {
            System.out.println("  B, before anything      : " + b.balance("alice"));
            a.begin();
            a.move("alice", "bob", 30);
            System.out.println("  A, own uncommitted work : " + a.balance("alice"));
            System.out.println("  B, at the same moment   : " + b.balance("alice"));
            a.commit();
            System.out.println("  B, after A committed    : " + b.balance("alice"));
            System.out.println();
            System.out.println("  B never saw the 70. That is read committed, and it is why");
            System.out.println("  a reader in another request cannot be handed a half-finished");
            System.out.println("  transfer and asked to make decisions about it");
        }
    }
}
