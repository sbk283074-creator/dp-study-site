public class Sol2 {
    static long factorialRecursive(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorialRecursive(n - 1);
    }

    static long factorialLoop(int n) {
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    public static void main(String[] args) {
        for (int n : new int[]{0, 1, 5, 10, 20}) {
            long recursive = factorialRecursive(n);
            long loop = factorialLoop(n);
            System.out.println(n + "! = " + recursive + "  (loop agrees: " + (recursive == loop) + ")");
        }
        System.out.println("20! still fits in a long : " + factorialLoop(20));
        System.out.println("21! overflows            : " + factorialLoop(21));
        System.out.println("and comes out negative   : " + (factorialLoop(21) < 0));
    }
}
