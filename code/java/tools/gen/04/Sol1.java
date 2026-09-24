public class Sol1 {
    public static void main(String[] args) {
        int a = 17, b = 5;
        int negative = -17;

        System.out.println("17 / 5          = " + (a / b));
        System.out.println("17 % 5          = " + (a % b));
        System.out.println("-17 / 5         = " + (negative / b));
        System.out.println("-17 % 5         = " + (negative % b));
        System.out.println("floorDiv(-17, 5)= " + Math.floorDiv(negative, b));
        System.out.println("floorMod(-17, 5)= " + Math.floorMod(negative, b));

        System.out.println("truncating and flooring differ only for negatives:");
        System.out.println("  floorDiv * 5 + floorMod = " + (Math.floorDiv(negative, b) * b + Math.floorMod(negative, b)));
        System.out.println("  /        * 5 + %        = " + ((negative / b) * b + (negative % b)));
    }
}
