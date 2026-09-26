import java.io.Serializable;

public class Stateful implements Serializable {
    private String user;
    private long expiresAt;

    public static void main(String[] args) {
        System.out.println("a session object that gets serialised into a store");
    }
}
