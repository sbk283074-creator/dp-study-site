import java.util.Arrays;

public class Scenario {
    static boolean sameItems(int[] a, int[] b) {
        return a == b;
    }

    static boolean sameItemsCorrect(int[] a, int[] b) {
        return Arrays.equals(a, b);
    }

    public static void main(String[] args) {
        int[] expected = {1, 2, 3};
        int[] actual = {1, 2, 3};

        System.out.println("both arrays print as " + Arrays.toString(expected)
                + " and " + Arrays.toString(actual));
        System.out.println("sameItems (==)           : " + sameItems(expected, actual));
        System.out.println("sameItemsCorrect (equals): " + sameItemsCorrect(expected, actual));

        int[] sameObject = expected;
        System.out.println("== is true only when both names hold one array: "
                + sameItems(expected, sameObject));
        System.out.println("so a test that compares a value with itself always passes: "
                + sameItems(expected, expected));
    }
}
