/** Sleeping, with the interrupt flag restored rather than swallowed. */
public final class Nap {

    private Nap() {
    }

    public static void millis(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
