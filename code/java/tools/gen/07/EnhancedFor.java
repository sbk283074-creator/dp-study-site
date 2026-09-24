import java.util.Arrays;

public class EnhancedFor {
    public static void main(String[] args) {
        int[] values = {4, 8, 15, 16, 23, 42};

        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        System.out.println("sum            = " + sum);

        System.out.print("values over 10 :");
        for (int value : values) {
            if (value > 10) {
                System.out.print(" " + value);
            }
        }
        System.out.println();

        for (int value : values) {
            value = value * 2;
        }
        System.out.println("after doubling the loop variable: " + Arrays.toString(values));

        for (int i = 0; i < values.length; i++) {
            values[i] = values[i] * 2;
        }
        System.out.println("after doubling by index         : " + Arrays.toString(values));

        for (int value : values) {
            if (value == 30) {
                System.out.println("found 30, but an enhanced for cannot say where");
            }
        }
    }
}
