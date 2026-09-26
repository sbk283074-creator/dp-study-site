import java.util.concurrent.Executors;

public class ZeroPool {
    public static void main(String[] args) {
        Executors.newFixedThreadPool(0);
    }
}
