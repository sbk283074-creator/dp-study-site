cat > Sol4.java <<'JAVA'
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class Sol4 {
    public static void main(String[] args) throws InterruptedException {
        ReentrantLock held = new ReentrantLock();
        held.lock();

        boolean got;
        try {
            got = held.tryLock(100, TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            got = false;
        }
        System.out.println("the same thread, tryLock on a lock it holds : " + got);
        System.out.println("hold count                                 : " + held.getHoldCount());

        held.unlock();
        held.unlock();
        System.out.println("after releasing both                       : " + held.getHoldCount());
        System.out.println();
        System.out.println("tryLock is reentrant too -- a thread may take a lock it");
        System.out.println("already holds. It is the *other* thread's lock it cannot have,");
        System.out.println("and there the timeout is what stops the program hanging");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
