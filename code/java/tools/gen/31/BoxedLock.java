public class BoxedLock {
    public static void main(String[] args) {
        Integer tickets = 1;
        synchronized (tickets) {
            System.out.println(tickets);
        }
    }
}
