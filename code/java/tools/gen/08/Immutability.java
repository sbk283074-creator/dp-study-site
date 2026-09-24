import java.util.Arrays;

public class Immutability {
    static final class Tags {
        private final String[] values;

        Tags(String... values) {
            this.values = values.clone();
        }

        String[] values() {
            return values.clone();
        }

        int count() {
            return values.length;
        }
    }

    public static void main(String[] args) {
        String[] input = {"alpha", "beta"};
        Tags tags = new Tags(input);

        input[0] = "changed";
        System.out.println("mutating the caller's array did not reach the object: "
                + Arrays.toString(tags.values()));

        String[] leaked = tags.values();
        leaked[0] = "leaked";
        System.out.println("mutating the returned array did not either:         "
                + Arrays.toString(tags.values()));

        System.out.println("count is still " + tags.count());
        System.out.println("without the two clone() calls the object would hold "
                + "whatever the caller did next");
    }
}
