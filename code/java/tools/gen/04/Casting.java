public class Casting {
    public static void main(String[] args) {
        double d = 3.99;
        System.out.println("(int) 3.99        = " + (int) d);
        System.out.println("(int) -3.99       = " + (int) -d);
        System.out.println("Math.round(3.99)  = " + Math.round(d));

        int threeHundred = 300;
        System.out.println("(byte) 300        = " + (byte) threeHundred);
        System.out.println("(short) 70000     = " + (short) 70000);
        System.out.println("(int) 4294967296L = " + (int) 4294967296L);

        long trillion = 1_000_000_000_000L;
        System.out.println("(int) 10^12       = " + (int) trillion);

        System.out.println("(char) 65         = " + (char) 65);
        System.out.println("(int) 'A'         = " + (int) 'A');

        float rounded = 16_777_217;
        System.out.println("float 16777217    = " + rounded);
        System.out.println("(int) that float  = " + (int) rounded);
        System.out.println("lost on the way   = " + (16_777_217 - (int) rounded));
    }
}
