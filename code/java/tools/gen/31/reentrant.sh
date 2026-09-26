cat > Reentrant.java <<'JAVA'
import java.util.concurrent.locks.ReentrantLock;

public class Reentrant {
    private static final ReentrantLock LOCK = new ReentrantLock();

    public static void main(String[] args) {
        System.out.println("before         : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        LOCK.lock();
        LOCK.lock();
        System.out.println("after 2 locks  : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        LOCK.unlock();
        System.out.println("after 1 unlock : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        LOCK.unlock();
        System.out.println("after 2 unlock : locked " + LOCK.isLocked()
                + ", hold count " + LOCK.getHoldCount());
        System.out.println();
        System.out.println("a monitor works the same way: a thread that holds it can enter");
        System.out.println("another block guarded by it, which is why one synchronized");
        System.out.println("method can call another on the same object without stopping");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Reentrant.java
java -cp out Reentrant
