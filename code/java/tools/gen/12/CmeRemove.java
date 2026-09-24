import java.util.ArrayList;
import java.util.List;

public class CmeRemove {

    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("ada", "bob", "cal", "ben"));

        for (String name : names) {
            if (name.startsWith("b")) {
                names.remove(name);
            }
        }

        System.out.println("never reached: " + names);
    }
}
