public class Scenario {
    static void swapWrong(int a, int b) {
        int temp = a;
        a = b;
        b = temp;
    }

    static void swapArray(int[] pair) {
        int temp = pair[0];
        pair[0] = pair[1];
        pair[1] = temp;
    }

    static final class Pair {
        int left;
        int right;

        Pair(int left, int right) {
            this.left = left;
            this.right = right;
        }

        @Override
        public String toString() {
            return "(" + left + ", " + right + ")";
        }
    }

    static void swapPair(Pair pair) {
        int temp = pair.left;
        pair.left = pair.right;
        pair.right = temp;
    }

    public static void main(String[] args) {
        int a = 1;
        int b = 2;
        swapWrong(a, b);
        System.out.println("after swapWrong(a, b): a = " + a + ", b = " + b);

        int[] pair = {1, 2};
        swapArray(pair);
        System.out.println("after swapArray:      " + pair[0] + ", " + pair[1]);

        Pair holder = new Pair(1, 2);
        swapPair(holder);
        System.out.println("after swapPair:       " + holder);

        System.out.println("only the two that received a reference changed the caller's state");
    }
}
