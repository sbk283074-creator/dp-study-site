import java.util.ArrayList;
import java.util.List;

public class CmeSilent {

    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("ada", "bob", "cal"));

        int examined = 0;
        for (String name : names) {
            examined++;
            if (name.startsWith("b")) {
                names.remove(name);
            }
        }

        System.out.println("no exception was thrown: " + names);
        System.out.println("elements examined: " + examined + " of 3");
        System.out.println("the last one was never looked at: " + (examined < 3));
    }
}
