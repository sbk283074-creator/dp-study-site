cat > Scenario.java <<'JAVA'
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.atomic.AtomicInteger;

public class Scenario {
    public static void main(String[] args) throws Exception {
        Map<String, String> plain = new HashMap<>();
        CyclicBarrier bothMissed = new CyclicBarrier(2);
        CyclicBarrier bothWrote = new CyclicBarrier(3);
        AtomicInteger builds = new AtomicInteger();

        Runnable racy = () -> {
            boolean missing = !plain.containsKey("report");
            JmmDemo.await(bothMissed);
            Nap.millis(50);
            if (missing) {
                plain.put("report", "built");
                builds.incrementAndGet();
            }
            JmmDemo.await(bothWrote);
        };
        Thread left = new Thread(racy);
        Thread right = new Thread(racy);
        left.start();
        right.start();
        JmmDemo.await(bothWrote);

        System.out.println("--- get-then-put from two threads ---");
        System.out.println("  times the report was built : " + builds.get());
        System.out.println("  entries in the map         : " + plain.size());
        System.out.println();

        ConcurrentHashMap<String, String> safe = new ConcurrentHashMap<>();
        AtomicInteger single = new AtomicInteger();
        int threads = 8;
        Thread[] pool = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            pool[i] = new Thread(() -> safe.computeIfAbsent("report", key -> {
                single.incrementAndGet();
                return "built";
            }));
        }
        for (Thread t : pool) {
            t.start();
        }
        for (Thread t : pool) {
            t.join();
        }

        System.out.println("--- computeIfAbsent from eight threads ---");
        System.out.println("  threads                    : " + threads);
        System.out.println("  times the report was built : " + single.get());
        System.out.println("  entries in the map         : " + safe.size());
        System.out.println();
        System.out.println("computeIfAbsent applies the function at most once per key,");
        System.out.println("which is the whole difference between a cache and a race");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
