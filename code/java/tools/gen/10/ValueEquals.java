import java.util.Objects;

public class ValueEquals {

    static final class Money {
        private final long cents;
        private final String currency;

        Money(long cents, String currency) {
            this.cents = cents;
            this.currency = Objects.requireNonNull(currency, "currency");
        }

        @Override
        public boolean equals(Object other) {
            if (this == other) {
                return true;
            }
            if (!(other instanceof Money money)) {
                return false;
            }
            return cents == money.cents && currency.equals(money.currency);
        }

        @Override
        public int hashCode() {
            return Objects.hash(cents, currency);
        }

        @Override
        public String toString() {
            return String.format("%s %.2f", currency, cents / 100.0);
        }
    }

    public static void main(String[] args) {
        Money a = new Money(1250, "GBP");
        Money b = new Money(1250, "GBP");
        Money c = new Money(1250, "USD");

        System.out.println("a prints as: " + a);
        System.out.println("a.equals(b), same value: " + a.equals(b));
        System.out.println("hashCodes agree: " + (a.hashCode() == b.hashCode()));
        System.out.println("a.equals(c), different currency: " + a.equals(c));
        System.out.println("a.equals(null): " + a.equals(null));
        System.out.println("a.equals(a String): " + a.equals("1250 GBP"));
    }
}
