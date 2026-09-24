public class Sol1 {
    static final class MinMax {
        final int min;
        final int max;
        final int indexOfMax;

        MinMax(int min, int max, int indexOfMax) {
            this.min = min;
            this.max = max;
            this.indexOfMax = indexOfMax;
        }
    }

    static MinMax minMax(int[] values) {
        int min = values[0];
        int max = values[0];
        int indexOfMax = 0;
        for (int i = 1; i < values.length; i++) {
            if (values[i] < min) {
                min = values[i];
            }
            if (values[i] > max) {
                max = values[i];
                indexOfMax = i;
            }
        }
        return new MinMax(min, max, indexOfMax);
    }

    public static void main(String[] args) {
        MinMax result = minMax(new int[]{7, 3, 9, 1, 9, 4});
        System.out.println("min          = " + result.min);
        System.out.println("max          = " + result.max);
        System.out.println("index of max = " + result.indexOfMax);
        System.out.println("a method returns one value, so the three answers travel in one object: "
                + (result.min < result.max));
    }
}
