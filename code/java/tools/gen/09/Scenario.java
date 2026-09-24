public class Scenario {
    interface Payment {
        String describe();
    }

    static final class Card implements Payment {
        @Override
        public String describe() {
            return "card, 3 day settlement";
        }
    }

    static final class BankTransfer implements Payment {
        @Override
        public String describe() {
            return "bank transfer, 1 day settlement";
        }
    }

    static final class Voucher implements Payment {
        @Override
        public String describe() {
            return "voucher, no settlement";
        }
    }

    static String describeWithChain(Object payment) {
        if (payment instanceof Card) {
            return "card, 3 day settlement";
        } else if (payment instanceof BankTransfer) {
            return "bank transfer, 1 day settlement";
        } else if (payment instanceof Voucher) {
            return "voucher, no settlement";
        }
        return "unknown payment";
    }

    public static void main(String[] args) {
        Payment[] payments = {new Card(), new BankTransfer(), new Voucher()};

        System.out.println("the chain and the objects agree on every known type:");
        for (Payment payment : payments) {
            System.out.println("  " + describeWithChain(payment) + "  |  " + payment.describe());
        }

        System.out.println("a fourth type the chain does not know about:");
        System.out.println("  the chain says: " + describeWithChain(new Object()));
        System.out.println("three branches for three implementations, and no way to tell they match");
    }
}
