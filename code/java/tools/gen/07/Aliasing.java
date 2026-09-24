import java.util.Arrays;

public class Aliasing {
    public static void main(String[] args) {
        int[] original = {1, 2, 3};
        int[] alias = original;
        int[] copy = Arrays.copyOf(original, original.length);
        int[] longer = Arrays.copyOf(original, 5);

        alias[0] = 99;

        System.out.println("original = " + Arrays.toString(original));
        System.out.println("alias    = " + Arrays.toString(alias));
        System.out.println("copy     = " + Arrays.toString(copy));
        System.out.println("longer   = " + Arrays.toString(longer));

        System.out.println("original == alias : " + (original == alias));
        System.out.println("original == copy  : " + (original == copy));

        int[] sameContents = {99, 2, 3};
        System.out.println("a different array holding the same numbers:");
        System.out.println("  ==            : " + (original == sameContents));
        System.out.println("  Arrays.equals : " + Arrays.equals(original, sameContents));
        System.out.println("  == is identity; Arrays.equals is contents");
    }
}
