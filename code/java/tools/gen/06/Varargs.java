public class Varargs {
    static int total(int... values) {
        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        return sum;
    }

    static String kinds(Object... items) {
        StringBuilder builder = new StringBuilder();
        for (Object item : items) {
            if (builder.length() > 0) {
                builder.append(", ");
            }
            builder.append(item.getClass().getSimpleName());
        }
        return builder.toString();
    }

    public static void main(String[] args) {
        System.out.println("total()        = " + total());
        System.out.println("total(1)       = " + total(1));
        System.out.println("total(1, 2, 3) = " + total(1, 2, 3));

        int[] array = {4, 5, 6};
        System.out.println("total(array)   = " + total(array));

        System.out.println("kinds(1, \"a\")  = " + kinds(1, "a"));
        System.out.println("kinds()        = [" + kinds() + "]");
        System.out.println("inside the method the vararg is an array of length " + array.length);
    }
}
