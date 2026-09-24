import java.util.Arrays;

public class Basics {
    public static void main(String[] args) {
        int[] zeros = new int[5];
        System.out.println("new int[5]     = " + Arrays.toString(zeros));

        String[] names = new String[3];
        System.out.println("new String[3]  = " + Arrays.toString(names));

        boolean[] flags = new boolean[2];
        System.out.println("new boolean[2] = " + Arrays.toString(flags));

        int[] literals = {10, 20, 30};
        System.out.println("literal        = " + Arrays.toString(literals));
        System.out.println("length         = " + literals.length);
        System.out.println("the last index is length - 1 = " + (literals.length - 1));

        System.out.println("without Arrays.toString it prints an identity, not the contents: "
                + literals.toString().startsWith("[I@"));
    }
}
