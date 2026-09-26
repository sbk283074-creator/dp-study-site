/** A clock the test moves by hand, so nothing depends on how fast the machine is. */
public final class Clock {

    private long now = 1_700_000_000_000L;

    public long now() {
        return now;
    }

    public void advance(long millis) {
        now += millis;
    }

    /** What a session does: expire when the clock passes its deadline. */
    public boolean expired(long expiresAt) {
        return now >= expiresAt;
    }
}
