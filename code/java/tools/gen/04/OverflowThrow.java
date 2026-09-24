public class OverflowThrow {
    public static void main(String[] args) {
        int half = Integer.MAX_VALUE / 2 + 1;
        int doubled = Math.multiplyExact(half, 2);
        System.out.println("this line is never reached: " + doubled);
    }
}
