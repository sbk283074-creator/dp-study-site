cat > Cas.java <<'JAVA'
import java.util.concurrent.atomic.AtomicInteger;

public class Cas {
    public static void main(String[] args) {
        AtomicInteger value = new AtomicInteger(5);

        System.out.println("start                       : " + value.get());
        System.out.println("compareAndSet(5, 9)         : " + value.compareAndSet(5, 9));
        System.out.println("compareAndSet(5, 9) again   : " + value.compareAndSet(5, 9));
        System.out.println("value                       : " + value.get());
        System.out.println("incrementAndGet             : " + value.incrementAndGet());
        System.out.println("getAndIncrement             : " + value.getAndIncrement());
        System.out.println("value                       : " + value.get());
        System.out.println("accumulateAndGet(3, max)    : " + value.accumulateAndGet(3, Math::max));
        System.out.println("updateAndGet(x -> x * 2)    : " + value.updateAndGet(x -> x * 2));
        System.out.println();
        System.out.println("the retry loop every atomic method is built from:");
        System.out.println("  addOne(value) = " + addOne(value));
        System.out.println("  value         = " + value.get());
    }

    static int addOne(AtomicInteger value) {
        int before;
        int after;
        do {
            before = value.get();
            after = before + 1;
        } while (!value.compareAndSet(before, after));
        return after;
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Cas.java
java -cp out Cas
