import java.util.HashMap;
import java.util.Map;

public class MutableKey {

    static final class Session {
        String user;

        Session(String user) {
            this.user = user;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Session s && s.user.equals(user);
        }

        @Override
        public int hashCode() {
            return user.hashCode();
        }

        @Override
        public String toString() {
            return "Session[" + user + "]";
        }
    }

    public static void main(String[] args) {
        Map<Session, Integer> visits = new HashMap<>();
        Session s = new Session("ada");
        visits.put(s, 1);
        System.out.println("lookup before the change: " + visits.get(s));

        s.user = "grace";
        System.out.println("the key now prints as: " + s);
        System.out.println("lookup after the change: " + visits.get(s));
        System.out.println("a fresh equal key finds it: " + visits.get(new Session("grace")));
        System.out.println("the map still holds: " + visits.size() + " entry");
        System.out.println("the value is still in there: " + visits.containsValue(1));
    }
}
