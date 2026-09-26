cat > Swallowed.java <<'EOF'
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class Swallowed {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(1);
        Future<?> quietly = pool.submit(() -> {
            throw new IllegalStateException("nobody will ever see this");
        });
        pool.shutdown();
        pool.awaitTermination(10, TimeUnit.SECONDS);

        System.out.println("the task is done    : " + quietly.isDone());
        System.out.println("anything printed?   : no");
        System.out.println("program exit status : 0");
        System.out.println();
        System.out.println("submit() does not rethrow. The exception is inside the Future,");
        System.out.println("and a Future nobody asks is a failure that never happened.");

        ExecutorService second = Executors.newFixedThreadPool(1);
        Future<?> asked = second.submit(() -> {
            throw new IllegalStateException("this one is collected");
        });
        try {
            asked.get();
        } catch (ExecutionException e) {
            System.out.println();
            System.out.println("asking gave back   : " + e.getCause().getClass().getSimpleName());
            System.out.println("with the message   : " + e.getCause().getMessage());
        }
        second.shutdown();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Swallowed.java
java -cp out Swallowed
