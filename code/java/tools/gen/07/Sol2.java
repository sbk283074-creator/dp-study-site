import java.util.Arrays;

public class Sol2 {
    static int[] histogram(int[] values, int buckets) {
        int[] counts = new int[buckets];
        for (int value : values) {
            if (value >= 0 && value < buckets) {
                counts[value]++;
            }
        }
        return counts;
    }

    public static void main(String[] args) {
        int[] values = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 0};
        int[] counts = histogram(values, 10);

        System.out.println("values = " + Arrays.toString(values));
        for (int value = 0; value < counts.length; value++) {
            if (counts[value] > 0) {
                System.out.println("  " + value + " appears " + counts[value] + " time(s)");
            }
        }

        int total = 0;
        for (int count : counts) {
            total += count;
        }
        System.out.println("the counts add up to " + total + " of " + values.length + " values");
    }
}
