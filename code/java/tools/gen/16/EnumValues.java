import java.util.Arrays;

public class EnumValues {
    enum Suit { CLUBS, DIAMONDS, HEARTS, SPADES }

    public static void main(String[] args) {
        Suit[] first = Suit.values();
        System.out.println("first        = " + Arrays.toString(first));

        first[0] = Suit.SPADES;
        System.out.println("after write  = " + Arrays.toString(first));
        System.out.println("fresh call   = " + Arrays.toString(Suit.values()));
        System.out.println("constants ok = " + (Suit.values()[0] == Suit.CLUBS));
        System.out.println("same array   = " + (Suit.values() == Suit.values()));
    }
}
