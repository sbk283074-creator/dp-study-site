public class Custom {

    static final class InsufficientFundsException extends Exception {
        private static final long serialVersionUID = 1L;

        private final long shortfall;

        InsufficientFundsException(long shortfall) {
            super("short by " + shortfall);
            this.shortfall = shortfall;
        }

        long shortfall() {
            return shortfall;
        }
    }

    static void withdraw(long balance, long amount) throws InsufficientFundsException {
        if (amount > balance) {
            throw new InsufficientFundsException(amount - balance);
        }
        System.out.println("withdrew " + amount);
    }

    public static void main(String[] args) throws InsufficientFundsException {
        withdraw(100, 40);

        try {
            withdraw(100, 250);
        } catch (InsufficientFundsException e) {
            System.out.println("message: " + e.getMessage());
            System.out.println("the shortfall travels as data: " + e.shortfall());
        }

        System.out.println("a checked exception cannot be ignored by a caller");
    }
}
