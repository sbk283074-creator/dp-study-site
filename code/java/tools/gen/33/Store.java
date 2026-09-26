import java.util.LinkedHashMap;
import java.util.Map;

/** The committed state of a small bank, shared by every connection to it. */
public final class Store {

    final Map<String, Long> committed = new LinkedHashMap<>();

    public void seed(String account, long balance) {
        committed.put(account, balance);
    }

    public Conn connect(String name) {
        return new Conn(this, name);
    }
}
