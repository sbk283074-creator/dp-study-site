cat > Sol1.java <<'EOF'
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Sol1 {
    public static void main(String[] args) throws InterruptedException {
        Work.reset();
        ExecutorService pool = Executors.newFixedThreadPool(4);
        for (int i = 0; i < 40; i++) {
            pool.execute(() -> {
                Work.sleep(5);
                Work.finish();
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("tasks      : 40");
        System.out.println("finished   : " + Work.done());
        System.out.println("threads    : " + Work.distinctThreads());
        System.out.println();
        System.out.println("the same loop, four threads: the pool is the only thing");
        System.out.println("that changed, and it is also the only bound on memory");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
