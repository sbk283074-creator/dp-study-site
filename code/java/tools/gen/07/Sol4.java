import java.util.Arrays;

public class Sol4 {
    static int secondLargest(int[] values) {
        int largest = Integer.MIN_VALUE;
        int second = Integer.MIN_VALUE;
        for (int value : values) {
            if (value > largest) {
                second = largest;
                largest = value;
            } else if (value < largest && value > second) {
                second = value;
            }
        }
        return second;
    }

    public static void main(String[] args) {
        int[][] cases = {{3, 7, 7, 2, 9, 9, 5}, {1, 2}, {5, 5, 5}, {-3, -7, -1}};
        for (int[] values : cases) {
            System.out.println(Arrays.toString(values) + " -> " + secondLargest(values));
        }

        System.out.println("a duplicate of the largest is not a second value: "
                + secondLargest(new int[]{4, 4, 1}));
        System.out.println("no second value at all reports Integer.MIN_VALUE: "
                + (secondLargest(new int[]{5, 5, 5}) == Integer.MIN_VALUE));
    }
}
