public class Encapsulated {
    static final class Open {
        int balanceCents;

        Open(int balanceCents) {
            this.balanceCents = balanceCents;
        }
    }

    static final class Guarded {
        private int balanceCents;

        Guarded(int balanceCents) {
            this.balanceCents = balanceCents;
        }

        int balanceCents() {
            return balanceCents;
        }

        boolean setBalanceCents(int cents) {
            if (cents < 0) {
                return false;
            }
            balanceCents = cents;
            return true;
        }
    }

    public static void main(String[] args) {
        Open open = new Open(100);
        open.balanceCents = -50;
        System.out.println("the open field now holds " + open.balanceCents);

        Guarded guarded = new Guarded(100);
        System.out.println("the guarded setter accepted -50: " + guarded.setBalanceCents(-50));
        System.out.println("the guarded balance is still    " + guarded.balanceCents());
        System.out.println("accepted 250: " + guarded.setBalanceCents(250)
                + ", balance now " + guarded.balanceCents());
    }
}
