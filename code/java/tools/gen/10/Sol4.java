import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Sol4 {

    static final class Ticket {
        final String id;
        final String assignee;

        Ticket(String id, String assignee) {
            this.id = Objects.requireNonNull(id, "id");
            this.assignee = assignee;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Ticket t
                    && id.equals(t.id)
                    && Objects.equals(assignee, t.assignee);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, assignee);
        }

        @Override
        public String toString() {
            return "Ticket[" + id + (assignee == null ? ", unassigned" : ", " + assignee) + "]";
        }
    }

    public static void main(String[] args) {
        Ticket open = new Ticket("T-1", null);
        Ticket alsoOpen = new Ticket("T-1", null);
        Ticket taken = new Ticket("T-1", "ada");

        boolean survived;
        try {
            survived = open.equals(alsoOpen);
        } catch (NullPointerException e) {
            survived = false;
        }

        System.out.println("two unassigned tickets are equal: " + open.equals(alsoOpen));
        System.out.println("their hashCodes agree: " + (open.hashCode() == alsoOpen.hashCode()));
        System.out.println("an assigned ticket differs: " + open.equals(taken));
        System.out.println("no NullPointerException from the null field: " + survived);

        Map<Ticket, String> log = new HashMap<>();
        log.put(open, "opened");
        System.out.println("lookup with an equal key holding a null: " + log.get(alsoOpen));
        System.out.println("printed: " + open);
        System.out.println("requireNonNull names the argument it rejected:");
        try {
            new Ticket(null, "ada");
        } catch (NullPointerException e) {
            System.out.println("  " + e.getMessage());
        }
    }
}
