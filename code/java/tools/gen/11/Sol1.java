import java.util.HashMap;
import java.util.Map;

public class Sol1 {

    static final class Key<T> {
        private final String name;

        Key(String name) {
            this.name = name;
        }

        @Override
        public String toString() {
            return name;
        }
    }

    static final class Registry {
        private final Map<Key<?>, Object> values = new HashMap<>();

        <T> void put(Key<T> key, T value) {
            values.put(key, value);
        }

        @SuppressWarnings("unchecked")
        <T> T get(Key<T> key) {
            return (T) values.get(key);
        }
    }

    static final Key<Integer> TIMEOUT = new Key<>("timeout");
    static final Key<String> HOST = new Key<>("host");

    public static void main(String[] args) {
        Registry registry = new Registry();
        registry.put(TIMEOUT, 30);
        registry.put(HOST, "example.com");

        System.out.println("host: " + registry.get(HOST));
        System.out.println("timeout plus one: " + (registry.get(TIMEOUT) + 1));
        System.out.println("no cast at the call site: " + registry.get(HOST).length());
        System.out.println("the key carries the type, not the caller: " + HOST);
    }
}
