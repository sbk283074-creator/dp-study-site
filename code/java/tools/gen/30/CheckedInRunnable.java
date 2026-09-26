public class CheckedInRunnable {
    public static void main(String[] args) {
        Runnable slow = () -> Thread.sleep(10);
        slow.run();
    }
}
