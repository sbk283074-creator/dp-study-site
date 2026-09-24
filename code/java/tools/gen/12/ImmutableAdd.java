import java.util.List;

public class ImmutableAdd {

    public static void main(String[] args) {
        List<String> fixed = List.of("a", "b");
        fixed.add("c");
        System.out.println("never reached: " + fixed);
    }
}
