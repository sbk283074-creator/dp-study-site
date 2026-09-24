public class MathOps {
    public static void main(String[] args) {
        System.out.println("abs(-5)          = " + Math.abs(-5));
        System.out.println("abs(MIN_VALUE)   = " + Math.abs(Integer.MIN_VALUE));
        System.out.println("min / max        = " + Math.min(3, 9) + " / " + Math.max(3, 9));
        System.out.println("pow(2, 10)       = " + Math.pow(2, 10));
        System.out.println("sqrt(2)          = " + Math.sqrt(2));
        System.out.println("hypot(3, 4)      = " + Math.hypot(3, 4));

        System.out.println("floorDiv(-7, 2)  = " + Math.floorDiv(-7, 2));
        System.out.println("floorMod(-7, 2)  = " + Math.floorMod(-7, 2));
        System.out.println("floorMod(7, -2)  = " + Math.floorMod(7, -2));
        System.out.println("-7 % 2           = " + (-7 % 2));

        System.out.println("round(2.5)       = " + Math.round(2.5));
        System.out.println("round(-2.5)      = " + Math.round(-2.5));
        System.out.println("ceil / floor     = " + Math.ceil(2.1) + " / " + Math.floor(2.9));
        System.out.println("clamp 15 to 10   = " + Math.clamp(15, 0, 10));
    }
}
