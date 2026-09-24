public class Exact {
    public static void main(String[] args) {
        System.out.println("addExact(1, 2)      = " + Math.addExact(1, 2));
        System.out.println("multiplyExact(6, 7) = " + Math.multiplyExact(6, 7));

        try {
            int bad = Math.addExact(Integer.MAX_VALUE, 1);
            System.out.println("unreachable: " + bad);
        } catch (ArithmeticException e) {
            System.out.println("addExact overflow       : " + e.getMessage());
        }

        try {
            System.out.println(Math.multiplyExact(1_000_000, 1_000_000));
        } catch (ArithmeticException e) {
            System.out.println("multiplyExact overflow  : " + e.getMessage());
        }

        try {
            System.out.println(Math.toIntExact(5_000_000_000L));
        } catch (ArithmeticException e) {
            System.out.println("toIntExact on a big long: " + e.getMessage());
        }

        System.out.println("and inside the range it just works: " + Math.toIntExact(5_000_000_000L - 4_999_999_999L));
    }
}
