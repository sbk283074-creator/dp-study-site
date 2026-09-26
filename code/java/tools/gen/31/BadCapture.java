public class BadCapture {
    public static void main(String[] args) {
        int seen = 0;
        Runnable task = () -> System.out.println(seen);
        seen++;
        task.run();
    }
}
