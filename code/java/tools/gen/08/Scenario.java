public class Scenario {
    static final class OpenWallet {
        int balanceCents;

        OpenWallet(int balanceCents) {
            this.balanceCents = balanceCents;
        }
    }

    static final class GuardedWallet {
        private int balanceCents;

        GuardedWallet(int balanceCents) {
            this.balanceCents = balanceCents;
        }

        int balanceCents() {
            return balanceCents;
        }

        boolean spend(int cents) {
            if (cents <= 0 || cents > balanceCents) {
                return false;
            }
            balanceCents -= cents;
            return true;
        }
    }

    public static void main(String[] args) {
        OpenWallet open = new OpenWallet(500);
        open.balanceCents -= 800;
        System.out.println("the open wallet holds " + open.balanceCents + " cents");

        GuardedWallet guarded = new GuardedWallet(500);
        System.out.println("spend 800 accepted: " + guarded.spend(800));
        System.out.println("the guarded wallet holds " + guarded.balanceCents() + " cents");

        System.out.println("nothing had to be added to break the first, and nothing can break the second");
    }
}
