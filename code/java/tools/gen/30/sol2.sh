cat > Sol2.java <<'EOF'
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class Sol2 {
    public static void main(String[] args) throws InterruptedException {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        Callable<Integer> work = () -> {
            Work.sleep(3_000);
            return 1;
        };

        Future<Integer> f = pool.submit(work);
        try {
            f.get(100, TimeUnit.MILLISECONDS);
            System.out.println("finished in time");
        } catch (TimeoutException e) {
            System.out.println("gave up waiting : " + e.getClass().getSimpleName());
        } catch (ExecutionException e) {
            System.out.println("task failed     : " + e.getCause().getMessage());
        }
        System.out.println("cancelled       : " + f.cancel(true));
        System.out.println("isDone after    : " + f.isDone());
        System.out.println();
        System.out.println("cancel(true) interrupts the worker; the task itself has to");
        System.out.println("notice, because interruption in Java is cooperative");
        pool.shutdownNow();
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
