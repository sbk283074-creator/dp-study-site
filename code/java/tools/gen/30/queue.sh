cat > Bounded.java <<'EOF'
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.RejectedExecutionHandler;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class Bounded {
    public static void main(String[] args) throws InterruptedException {
        run("AbortPolicy", new ThreadPoolExecutor.AbortPolicy());
        System.out.println();
        run("CallerRunsPolicy", new ThreadPoolExecutor.CallerRunsPolicy());
    }

    static void run(String label, RejectedExecutionHandler policy)
            throws InterruptedException {
        Work.reset();
        int rejected = 0;

        ThreadPoolExecutor pool = new ThreadPoolExecutor(
                2, 2, 0, TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(5), policy);

        for (int i = 0; i < 12; i++) {
            try {
                pool.execute(() -> {
                    Work.sleep(200);
                    Work.finish();
                });
            } catch (RejectedExecutionException e) {
                rejected++;
            }
        }
        pool.shutdown();
        pool.awaitTermination(60, TimeUnit.SECONDS);

        System.out.println("policy          : " + label);
        System.out.println("submitted       : 12");
        System.out.println("rejected        : " + rejected);
        System.out.println("actually ran    : " + Work.done());
        System.out.println("ran on caller   : " + onThread("main"));
    }

    static int onThread(String wanted) {
        int n = 0;
        for (String name : Work.threadNames()) {
            if (name.equals(wanted)) {
                n++;
            }
        }
        return n;
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Bounded.java
java -cp out Bounded
