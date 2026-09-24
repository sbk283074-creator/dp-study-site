public class Sol4 {
    static int gcdRecursive(int a, int b) {
        return b == 0 ? a : gcdRecursive(b, a % b);
    }

    static int gcdLoop(int a, int b) {
        while (b != 0) {
            int remainder = a % b;
            a = b;
            b = remainder;
        }
        return a;
    }

    public static void main(String[] args) {
        int[][] pairs = {{48, 18}, {17, 5}, {100, 0}, {0, 7}, {270, 192}};
        for (int[] pair : pairs) {
            int recursive = gcdRecursive(pair[0], pair[1]);
            int loop = gcdLoop(pair[0], pair[1]);
            System.out.println("gcd(" + pair[0] + ", " + pair[1] + ") = " + recursive
                    + "  (loop agrees: " + (recursive == loop) + ")");
        }
        System.out.println("a base case of b == 0 is what makes both versions stop: "
                + (gcdRecursive(100, 0) == 100));
    }
}
