import java.util.function.Function;

public class Box {

    static final class Holder<T> {
        private final T value;

        Holder(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }

        <R> Holder<R> map(Function<T, R> step) {
            return new Holder<>(step.apply(value));
        }

        @Override
        public String toString() {
            return "Holder[" + value + "]";
        }
    }

    public static void main(String[] args) throws Exception {
        Holder<String> name = new Holder<>("Ada");
        Holder<Integer> count = new Holder<>(3);

        System.out.println("name: " + name);
        System.out.println("count: " + count);
        System.out.println("a String with no cast: " + name.get().toUpperCase());
        System.out.println("an Integer with no cast: " + (count.get() + 1));

        Holder<Integer> length = name.map(String::length);
        System.out.println("mapped: " + length);
        System.out.println("the erased return type of get(): "
                + Holder.class.getDeclaredMethod("get").getReturnType());
    }
}
