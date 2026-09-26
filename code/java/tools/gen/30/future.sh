cat > Futures.java <<'EOF'
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class Futures {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(2);

        Future<Integer> quick = pool.submit(() -> {
            Work.sleep(20);
            return 6 * 7;
        });

        System.out.println("immediately after submit, isDone: " + quick.isDone());
        System.out.println("get() blocks until it is        : " + quick.get());
        System.out.println("and then isDone                 : " + quick.isDone());

        Future<Integer> slow = pool.submit(() -> {
            Work.sleep(5_000);
            return 1;
        });
        try {
            slow.get(50, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            System.out.println();
            System.out.println("a bounded wait gave up with     : "
                    + e.getClass().getSimpleName());
        }

        Future<?> broken = pool.submit(() -> {
            throw new IllegalStateException("the downstream refused");
        });
        try {
            broken.get();
        } catch (ExecutionException e) {
            System.out.println("the task's own exception arrived as: "
                    + e.getClass().getSimpleName());
            System.out.println("and its cause is                   : "
                    + e.getCause().getClass().getSimpleName());
            System.out.println("with the message                   : "
                    + e.getCause().getMessage());
        }

        pool.shutdownNow();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Futures.java
java -cp out Futures
