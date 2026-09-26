cat > Sol3.java <<'JAVA'
public class Sol3 {
    public static void main(String[] args) {
        Bounded pool = new Bounded(3);
        System.out.println("borrow 1 : " + pool.borrow());
        System.out.println("borrow 2 : " + pool.borrow());
        System.out.println("borrow 3 : " + pool.borrow());
        System.out.println("borrow 4 : " + pool.borrow());
        pool.giveBack();
        System.out.println("after one comes back : " + pool.borrow());
        System.out.println();
        System.out.println("a pool test that needed a timeout would be a flaky test. This one");
        System.out.println("is a state machine, so it is either right or wrong, instantly");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
