import java.util.HashMap;
import java.util.Map;

public class Scenario {

    static final class Customer {
        final String email;

        Customer(String email) {
            this.email = email;
        }
    }

    static Map<Customer, Integer> countOrders(String[] emails) {
        Map<Customer, Integer> counts = new HashMap<>();
        for (String email : emails) {
            Customer key = new Customer(email);
            counts.put(key, counts.getOrDefault(key, 0) + 1);
        }
        return counts;
    }

    public static void main(String[] args) {
        String[] emails = {
            "ada@example.com", "grace@example.com", "ada@example.com",
            "ada@example.com", "grace@example.com"
        };

        Map<Customer, Integer> counts = countOrders(emails);
        int largest = counts.values().stream().mapToInt(Integer::intValue).max().orElse(0);
        long distinctEmails = java.util.Arrays.stream(emails).distinct().count();

        System.out.println("orders received: " + emails.length);
        System.out.println("distinct customers reported: " + counts.size());
        System.out.println("customers actually present: " + distinctEmails);
        System.out.println("the largest count in the report: " + largest);
        System.out.println("every row in the report reads 1: " + (largest == 1));
    }
}
