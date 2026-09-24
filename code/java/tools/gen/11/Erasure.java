import java.util.ArrayList;
import java.util.List;

public class Erasure {

    static final class Holder<T> {
        private final T value;

        Holder(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }
    }

    public static void main(String[] args) throws Exception {
        List<String> words = new ArrayList<>();
        List<Integer> numbers = new ArrayList<>();

        System.out.println("words.getClass(): " + words.getClass().getName());
        System.out.println("numbers.getClass(): " + numbers.getClass().getName());
        System.out.println("one class object for both: "
                + (words.getClass() == numbers.getClass()));

        System.out.println("List.get returns: "
                + List.class.getMethod("get", int.class).getReturnType().getName());
        System.out.println("Holder.get returns: "
                + Holder.class.getDeclaredMethod("get").getReturnType().getName());
        System.out.println("Holder's field is a: "
                + Holder.class.getDeclaredFields()[0].getType().getName());
    }
}
