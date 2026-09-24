import java.util.Arrays;

public class Chaining {

    static int parsePort(String text) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("bad port: " + text, e);
        }
    }

    public static void main(String[] args) {
        try {
            parsePort("http");
        } catch (IllegalArgumentException e) {
            System.out.println("message: " + e.getMessage());
            System.out.println("cause: " + e.getCause().getClass().getName());
            System.out.println("the cause kept its own message: " + e.getCause().getMessage());
            System.out.println("frames naming parseInt in the cause: "
                    + Arrays.stream(e.getCause().getStackTrace())
                            .filter(f -> f.getMethodName().equals("parseInt")).count());
        }
    }
}
