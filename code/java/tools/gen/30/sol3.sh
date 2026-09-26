cat > Sol3.java <<'JAVA'
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class Sol3 {
    public static void main(String[] args) throws InterruptedException {
        List<String> order = Collections.synchronizedList(new ArrayList<>());
        ExecutorService pool = Executors.newFixedThreadPool(3);

        for (int i = 0; i < 9; i++) {
            final int n = i;
            pool.execute(() -> {
                Work.sleep(n == 0 ? 200 : 1);
                order.add("task " + n);
            });
        }
        pool.shutdown();
        pool.awaitTermination(30, TimeUnit.SECONDS);

        System.out.println("submitted in order : task 0 first, task 8 last");
        System.out.println("task 0 finished in : position "
                + (order.indexOf("task 0") + 1) + " of 9");
        System.out.println("tasks finished     : " + order.size());
        System.out.println("threads used       : " + Work.distinctThreads());
        System.out.println();
        System.out.println("submission order is not completion order, and it never was:");
        System.out.println("a pool may start your tasks in any order it likes, and finish");
        System.out.println("them in whatever order the work allows");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
