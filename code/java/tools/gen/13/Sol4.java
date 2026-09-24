import java.util.HashMap;
import java.util.Map;

public class Sol4 {

    static final class ServiceException extends RuntimeException {
        private static final long serialVersionUID = 1L;

        ServiceException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    static int lookup(Map<String, Integer> table, String key) {
        try {
            return table.get(key).intValue();
        } catch (NullPointerException e) {
            throw new ServiceException("no entry for key '" + key + "'", e);
        }
    }

    public static void main(String[] args) {
        Map<String, Integer> table = new HashMap<>();
        table.put("a", 1);

        System.out.println("a -> " + lookup(table, "a"));

        try {
            lookup(table, "zzz");
        } catch (ServiceException e) {
            System.out.println("message: " + e.getMessage());
            System.out.println("cause: " + e.getCause().getClass().getName());
            System.out.println("the wrapper is unchecked, so no signature changed: "
                    + (e instanceof RuntimeException));
        }
    }
}
