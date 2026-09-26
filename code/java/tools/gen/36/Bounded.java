/** A two-slot stand-in for a pool, small enough to test without timing. */
public final class Bounded {

    private final int max;
    private int inUse;

    public Bounded(int max) {
        this.max = max;
    }

    public boolean borrow() {
        if (inUse >= max) {
            return false;
        }
        inUse++;
        return true;
    }

    public void giveBack() {
        if (inUse > 0) {
            inUse--;
        }
    }

    public int size() {
        return max;
    }
}
