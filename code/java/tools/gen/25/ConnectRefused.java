import java.net.ConnectException;
import java.net.ServerSocket;
import java.net.Socket;

public class ConnectRefused {
    public static void main(String[] args) throws Exception {
        int closedPort;
        try (ServerSocket probe = new ServerSocket(0)) {
            closedPort = probe.getLocalPort();
        }

        try (Socket socket = new Socket("127.0.0.1", closedPort)) {
            System.out.println("connected=" + socket.isConnected() + ", which cannot happen");
        } catch (ConnectException e) {
            System.out.println("the port was bound, then closed, then dialled again");
            System.out.println("ConnectException: " + e.getMessage());
            System.out.println("the address is not in the message, which is why this is stable");
        }
    }
}
