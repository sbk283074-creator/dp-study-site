import java.util.Arrays;

public class Sol1 {
    static void reverse(int[] values) {
        int left = 0;
        int right = values.length - 1;
        while (left < right) {
            int temp = values[left];
            values[left] = values[right];
            values[right] = temp;
            left++;
            right--;
        }
    }

    public static void main(String[] args) {
        int[][] cases = {{1}, {1, 2}, {1, 2, 3}, {1, 2, 3, 4}, {1, 2, 3, 4, 5}};
        for (int[] values : cases) {
            int[] before = Arrays.copyOf(values, values.length);
            reverse(values);
            System.out.println(Arrays.toString(before) + " -> " + Arrays.toString(values));
        }

        int[] odd = {1, 2, 3, 4, 5};
        reverse(odd);
        System.out.println("for an odd length the middle element never moves: " + odd[2]);
        System.out.println("the swap uses the array, so it works where a swap method could not");
    }
}
