cat > Sol2.java <<'JAVA'
import java.util.concurrent.atomic.AtomicInteger;

public class Sol2 {
    public static void main(String[] args) {
        AtomicInteger value = new AtomicInteger(0);
        int delta = 25;

        int before;
        int after;
        do {
            before = value.get();
            after = before + delta;
        } while (!value.compareAndSet(before, after));

        System.out.println("read             : " + before);
        System.out.println("wrote            : " + after);
        System.out.println("compareAndSet    : true");
        System.out.println("value            : " + value.get());
        System.out.println();
        System.out.println("the loop is the point: a CAS says \"set this to that only if it");
        System.out.println("is still what I saw\", and the retry is what makes that correct");
        System.out.println("under contention rather than merely optimistic");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
