import java.util.ArrayList;
import java.util.List;

public class RawTypes {

    public static void main(String[] args) {
        List<String> typed = new ArrayList<>();
        typed.add("one");

        List raw = typed;
        raw.add(42);

        System.out.println("the raw list is the typed list: " + (raw == typed));
        System.out.println("the typed view now holds: " + typed);
        System.out.println("and its size is: " + typed.size());
    }
}
