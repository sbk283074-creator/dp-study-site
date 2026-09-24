public class Sol2 {
    static final class Money {
        private final long cents;

        private Money(long cents) {
            this.cents = cents;
        }

        static Money of(long cents) {
            return new Money(cents);
        }

        Money plus(Money other) {
            return new Money(cents + other.cents);
        }

        Money minus(Money other) {
            return new Money(cents - other.cents);
        }

        Money times(int factor) {
            return new Money(cents * factor);
        }

        long cents() {
            return cents;
        }

        @Override
        public String toString() {
            return (cents / 100) + "." + String.format("%02d", Math.abs(cents % 100));
        }
    }

    public static void main(String[] args) {
        Money price = Money.of(1_299);
        Money shipping = Money.of(499);

        System.out.println("price         = " + price);
        System.out.println("shipping      = " + shipping);
        System.out.println("plus          = " + price.plus(shipping));
        System.out.println("times 3       = " + price.times(3));
        System.out.println("price after all of that = " + price);
        System.out.println("and a negative amount is representable: "
                + Money.of(100).minus(Money.of(250)));
    }
}
