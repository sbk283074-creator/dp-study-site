import java.io.IOException;

public class UnhandledChecked {

    static String read() throws IOException {
        throw new IOException("disk gone");
    }

    public static void main(String[] args) {
        System.out.println(read());
    }
}
