import java.util.HashMap;
import java.util.Map;

public class Scenario {

    static final class Registry {
        private final Map<String, Object> values = new HashMap<>();

        void put(String key, Object value) {
            values.put(key, value);
        }

        Object get(String key) {
            return values.get(key);
        }

        int size() {
            return values.size();
        }
    }

    public static void main(String[] args) {
        Registry registry = new Registry();
        registry.put("timeout", 30);
        registry.put("host", "example.com");

        System.out.println("host: " + (String) registry.get("host"));
        System.out.println("host length: " + ((String) registry.get("host")).length());

        try {
            int timeout = (Integer) registry.get("host");
            System.out.println("never reached: " + timeout);
        } catch (ClassCastException e) {
            System.out.println("the cast fails where it is read, not where it was written");
        }

        System.out.println("keys stored: " + registry.size());
    }
}
