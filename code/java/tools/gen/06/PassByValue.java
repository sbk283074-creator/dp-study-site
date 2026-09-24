public class PassByValue {
    static void tryToReassign(int number, int[] numbers) {
        number = 999;
        numbers = new int[]{999};
    }

    static void mutate(int[] numbers) {
        numbers[0] = 42;
    }

    public static void main(String[] args) {
        int value = 1;
        tryToReassign(value, new int[]{1});
        System.out.println("after tryToReassign, the caller's int is still " + value);

        int[] shared = {1, 2, 3};
        mutate(shared);
        System.out.println("after mutate, the caller's array starts with " + shared[0]);

        int[] original = {1, 2, 3};
        int[] alias = original;
        alias[0] = 99;
        System.out.println("the alias and the original are the same array: " + (original[0] == 99));

        int[] copy = original.clone();
        copy[0] = 7;
        System.out.println("a clone is a different array: " + (original[0] != copy[0]));
        System.out.println("original[0] = " + original[0] + ", copy[0] = " + copy[0]);
    }
}
