import java.util.HashSet;
import java.util.Set;

public class EqualityInSets {

    static final class WithoutEquals {
        final String id;

        WithoutEquals(String id) {
            this.id = id;
        }
    }

    record WithEquals(String id) {
    }

    public static void main(String[] args) {
        Set<WithoutEquals> identity = new HashSet<>();
        identity.add(new WithoutEquals("A"));
        identity.add(new WithoutEquals("A"));

        Set<WithEquals> value = new HashSet<>();
        value.add(new WithEquals("A"));
        value.add(new WithEquals("A"));

        System.out.println("identity keys give: " + identity.size() + " entries");
        System.out.println("value keys give: " + value.size() + " entry");
        System.out.println("contains on the identity set: "
                + identity.contains(new WithoutEquals("A")));
        System.out.println("contains on the value set: "
                + value.contains(new WithEquals("A")));
    }
}
