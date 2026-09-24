public class Account {
    private long balanceCents;
    private final String owner;

    Account(String owner, long openingCents) {
        this.owner = owner;
        this.balanceCents = openingCents;
    }

    String owner() {
        return owner;
    }

    long balanceCents() {
        return balanceCents;
    }

    void deposit(long cents) {
        if (cents <= 0) {
            throw new IllegalArgumentException("deposit must be positive: " + cents);
        }
        balanceCents += cents;
    }

    boolean withdraw(long cents) {
        if (cents <= 0 || cents > balanceCents) {
            return false;
        }
        balanceCents -= cents;
        return true;
    }

    @Override
    public String toString() {
        return owner + " holds " + balanceCents + " cents";
    }

    public static void main(String[] args) {
        Account account = new Account("ada", 5_000);
        System.out.println(account);

        account.deposit(2_500);
        System.out.println("after deposit:   " + account);

        System.out.println("withdraw 1000    = " + account.withdraw(1_000));
        System.out.println("withdraw 999999  = " + account.withdraw(999_999));
        System.out.println("after attempts:  " + account);

        try {
            account.deposit(-1);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        System.out.println("the balance never went negative: " + (account.balanceCents() >= 0));
    }
}
