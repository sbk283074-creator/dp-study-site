cat > PerTask.java <<'EOF'
public class PerTask {
    public static void main(String[] args) throws InterruptedException {
        int tasks = 100;
        Work.reset();

        long start = System.nanoTime();
        Thread[] threads = new Thread[tasks];
        for (int i = 0; i < tasks; i++) {
            threads[i] = new Thread(() -> {
                Work.sleep(20);
                Work.finish();
            });
            threads[i].start();
        }
        for (Thread t : threads) {
            t.join();
        }
        long millis = (System.nanoTime() - start) / 1_000_000L;

        System.out.println("tasks           : " + tasks);
        System.out.println("threads created : " + Work.distinctThreads());
        System.out.println("tasks finished  : " + Work.done());
        System.out.println("wall under 1s   : " + (millis < 1000));
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out PerTask.java
java -cp out PerTask
