import java.util.Arrays;

public class Sorting {
    public static void main(String[] args) {
        int[] values = {42, 8, 15, 4, 23, 16};
        System.out.println("unsorted         = " + Arrays.toString(values));
        Arrays.sort(values);
        System.out.println("sorted           = " + Arrays.toString(values));

        System.out.println("binarySearch(23) = " + Arrays.binarySearch(values, 23));
        System.out.println("binarySearch(7)  = " + Arrays.binarySearch(values, 7));

        int[] filled = new int[5];
        Arrays.fill(filled, 7);
        System.out.println("filled           = " + Arrays.toString(filled));
        Arrays.fill(filled, 1, 3, 0);
        System.out.println("filled 1 to 2    = " + Arrays.toString(filled));

        String[] words = {"pear", "apple", "fig"};
        Arrays.sort(words);
        System.out.println("strings sort     = " + Arrays.toString(words));

        int[] unsorted = {3, 1, 2};
        System.out.println("searching an unsorted array: " + Arrays.binarySearch(unsorted, 3));
        System.out.println("3 is at index 0, and binary search reported " + Arrays.binarySearch(unsorted, 3));
    }
}
