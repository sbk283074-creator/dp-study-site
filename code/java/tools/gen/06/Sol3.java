public class Sol3 {
    static int search(int[] sorted, int target) {
        return search(sorted, target, 0, sorted.length - 1);
    }

    private static int search(int[] sorted, int target, int low, int high) {
        if (low > high) {
            return -1;
        }
        int mid = low + (high - low) / 2;
        if (sorted[mid] == target) {
            return mid;
        }
        if (sorted[mid] < target) {
            return search(sorted, target, mid + 1, high);
        }
        return search(sorted, target, low, mid - 1);
    }

    public static void main(String[] args) {
        int[] sorted = {1, 3, 5, 7, 9, 11, 13};
        for (int target : new int[]{1, 7, 13, 4}) {
            System.out.println("search(" + target + ") = " + search(sorted, target));
        }

        int low = 1_500_000_000;
        int high = 1_800_000_000;
        System.out.println("(low + high) / 2      = " + ((low + high) / 2));
        System.out.println("low + (high - low) / 2 = " + (low + (high - low) / 2));
    }
}
