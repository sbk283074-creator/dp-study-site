public class Compact {
    record Range(int lo, int hi) {
        Range {
            if (lo > hi) {
                throw new IllegalArgumentException("lo " + lo + " is above hi " + hi);
            }
        }
    }

    record Name(String first, String last) {
        Name {
            first = first.trim();
            last = last.trim();
            if (first.isEmpty()) {
                throw new IllegalArgumentException("first name is blank");
            }
        }

        String full() {
            return first + " " + last;
        }
    }

    public static void main(String[] args) {
        System.out.println("range      = " + new Range(2, 9));
        System.out.println("normalised = " + new Name("  Ada ", "  Lovelace ").full());

        try {
            new Range(9, 2);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected   = " + e.getMessage());
        }
    }
}
