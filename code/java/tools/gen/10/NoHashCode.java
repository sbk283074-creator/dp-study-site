import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class NoHashCode {

    static final class Badge {
        final String code;

        Badge(String code) {
            this.code = code;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Badge badge && badge.code.equals(code);
        }
    }

    public static void main(String[] args) {
        Badge issued = new Badge("A-17");
        Badge lookedUp = new Badge("A-17");

        System.out.println("equals says they are the same: " + issued.equals(lookedUp));

        Set<Badge> seen = new HashSet<>();
        seen.add(issued);
        seen.add(lookedUp);
        System.out.println("a set of equal values holds: " + seen.size() + " entries");

        Map<Badge, String> owner = new HashMap<>();
        owner.put(issued, "Ada");
        System.out.println("map.get with an equal key: " + owner.get(lookedUp));
        System.out.println("the map still holds: " + owner.size() + " entry");
    }
}
