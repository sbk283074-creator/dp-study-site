public class Sol3 {
    static int clamp(int value, int low, int high) {
        return Math.max(low, Math.min(high, value));
    }

    public static void main(String[] args) {
        int[][] cases = {
            {5, 1, 10, 5},
            {0, 1, 10, 1},
            {11, 1, 10, 10},
            {1, 1, 10, 1},
            {10, 1, 10, 10},
        };

        int failed = 0;
        for (int[] c : cases) {
            int actual = clamp(c[0], c[1], c[2]);
            boolean ok = actual == c[3];
            if (!ok) {
                failed++;
            }
            System.out.printf("%-4s clamp(%2d, %2d, %2d) = %2d%n",
                    ok ? "PASS" : "FAIL", c[0], c[1], c[2], actual);
        }
        System.out.println("failed " + failed + " of " + cases.length);
    }
}
