public class Sol2 {
    static int clamp(int value, int min, int max) {
        if (value < min) {
            return min;
        }
        if (value > max) {
            return max;
        }
        return value;
    }

    public static void main(String[] args) {
        int[] samples = {-5, 0, 7, 10, 15};
        boolean agree = true;
        for (int value : samples) {
            int hand = clamp(value, 0, 10);
            int builtIn = Math.clamp(value, 0, 10);
            agree = agree && hand == builtIn;
            System.out.println("value " + value + " -> hand " + hand + ", Math.clamp " + builtIn);
        }
        System.out.println("the two agree on every case above: " + agree);

        String verdict;
        try {
            verdict = "returned " + Math.clamp(5, 10, 0);
        } catch (IllegalArgumentException e) {
            verdict = "threw " + e.getMessage();
        }
        System.out.println("swapped bounds: hand returned " + clamp(5, 10, 0) + ", Math.clamp " + verdict);
    }
}
