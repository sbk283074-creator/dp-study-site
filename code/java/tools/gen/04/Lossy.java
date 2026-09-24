public class Lossy {
    public static void main(String[] args) {
        int big = 100_000;
        byte small = 0;
        small += big;
        System.out.println("100000 squeezed into a byte: " + small);
    }
}
