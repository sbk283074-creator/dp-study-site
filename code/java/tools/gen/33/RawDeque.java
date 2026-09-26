import java.util.ArrayDeque;
import java.util.Deque;

public class RawDeque {
    public static void main(String[] args) {
        Deque free = new ArrayDeque();
        free.push("connection-1");
        System.out.println(free.pop());
    }
}
