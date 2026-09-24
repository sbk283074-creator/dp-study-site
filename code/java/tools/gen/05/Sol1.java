public class Sol1 {
    static String fizzbuzz(int n) {
        if (n % 15 == 0) {
            return "FizzBuzz";
        }
        if (n % 3 == 0) {
            return "Fizz";
        }
        if (n % 5 == 0) {
            return "Buzz";
        }
        return String.valueOf(n);
    }

    public static void main(String[] args) {
        for (int n = 1; n <= 20; n++) {
            System.out.print(fizzbuzz(n) + (n == 20 ? "" : " "));
        }
        System.out.println();
        System.out.println("multiples of fifteen up to 100: " + count(100, 15));
        System.out.println("multiples of three  up to 100: " + count(100, 3));
        System.out.println("multiples of five   up to 100: " + count(100, 5));
    }

    static int count(int limit, int step) {
        int total = 0;
        for (int n = step; n <= limit; n += step) {
            total++;
        }
        return total;
    }
}
