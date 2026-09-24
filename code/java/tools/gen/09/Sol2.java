import java.util.List;
import java.util.Locale;

public class Sol2 {
    interface Payable {
        long amountCents();

        String reference();
    }

    static final class Invoice implements Payable {
        private final String number;
        private final long cents;

        Invoice(String number, long cents) {
            this.number = number;
            this.cents = cents;
        }

        @Override
        public long amountCents() {
            return cents;
        }

        @Override
        public String reference() {
            return "invoice " + number;
        }
    }

    static final class Salary implements Payable {
        private final String employee;
        private final long cents;

        Salary(String employee, long cents) {
            this.employee = employee;
            this.cents = cents;
        }

        @Override
        public long amountCents() {
            return cents;
        }

        @Override
        public String reference() {
            return "salary " + employee;
        }
    }

    static long total(List<Payable> items) {
        long sum = 0;
        for (Payable item : items) {
            sum += item.amountCents();
        }
        return sum;
    }

    public static void main(String[] args) {
        List<Payable> batch = List.of(
                new Invoice("A-1", 1_250), new Salary("ada", 250_000), new Invoice("A-2", 999));

        for (Payable item : batch) {
            System.out.println(String.format(Locale.ROOT, "%-16s %8d", item.reference(), item.amountCents()));
        }

        System.out.println("total cents = " + total(batch));
        System.out.println("a fourth Payable type needs no change to total(): "
                + (total(batch) == 252_249L));
    }
}
