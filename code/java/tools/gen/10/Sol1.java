import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Sol1 {

    static final class Customer {
        final String email;

        Customer(String email) {
            this.email = Objects.requireNonNull(email, "email");
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Customer c && c.email.equals(email);
        }

        @Override
        public int hashCode() {
            return email.hashCode();
        }

        @Override
        public String toString() {
            return email;
        }
    }

    public static void main(String[] args) {
        String[] emails = {
            "ada@example.com", "grace@example.com", "ada@example.com",
            "ada@example.com", "grace@example.com"
        };

        Map<Customer, Integer> counts = new HashMap<>();
        for (String email : emails) {
            counts.merge(new Customer(email), 1, Integer::sum);
        }

        System.out.println("orders received: " + emails.length);
        System.out.println("distinct customers reported: " + counts.size());
        System.out.println("ada's count: " + counts.get(new Customer("ada@example.com")));
        System.out.println("grace's count: " + counts.get(new Customer("grace@example.com")));
        System.out.println("the counts add back to the input: "
                + (counts.values().stream().mapToInt(Integer::intValue).sum() == emails.length));
    }
}
