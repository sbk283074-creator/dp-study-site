public class Overflow {
    public static void main(String[] args) {
        System.out.println("MAX_VALUE      = " + Integer.MAX_VALUE);
        System.out.println("MAX_VALUE + 1  = " + (Integer.MAX_VALUE + 1));
        System.out.println("MIN_VALUE      = " + Integer.MIN_VALUE);
        System.out.println("MIN_VALUE - 1  = " + (Integer.MIN_VALUE - 1));
        System.out.println("wrapped to the far end: " + (Integer.MAX_VALUE + 1 == Integer.MIN_VALUE));

        int million = 1_000_000;
        System.out.println("1e6 * 1e6 as int  = " + (million * million));
        System.out.println("1e6 * 1e6 as long = " + (1_000_000L * 1_000_000L));

        int total = 0;
        for (int i = 0; i < 5; i++) {
            total += 1_500_000_000;
        }
        System.out.println("5 x 1.5e9 as int  = " + total);
        System.out.println("5 x 1.5e9 as long = " + (5L * 1_500_000_000L));

        long correct = 1_000_000L * 1_000_000L;
        System.out.println("the long answer is right: " + (correct == 1_000_000_000_000L));
    }
}
