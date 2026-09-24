import java.util.List;

public class InstanceOfGeneric {

    static boolean isStringList(Object value) {
        return value instanceof List<String>;
    }

    public static void main(String[] args) {
        System.out.println(isStringList(List.of("a")));
    }
}
