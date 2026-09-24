public class Sol3 {
    public static void main(String[] args) {
        int n = 1;
        while (n * n >= 0) {
            n++;
        }
        System.out.println("smallest n whose square is negative: " + n);
        System.out.println("n * n                               = " + (n * n));
        System.out.println("(long) n * n                        = " + ((long) n * n));
        System.out.println("previous n still safe: " + ((n - 1) + " * " + (n - 1) + " = " + ((n - 1) * (n - 1))));
        System.out.println("sqrt of the true square             = " + Math.sqrt((long) n * n));
    }
}
