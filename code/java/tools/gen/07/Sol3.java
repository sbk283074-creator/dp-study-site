import java.util.Arrays;

public class Sol3 {
    static int[][] transpose(int[][] matrix) {
        int[][] result = new int[matrix[0].length][matrix.length];
        for (int row = 0; row < matrix.length; row++) {
            for (int col = 0; col < matrix[row].length; col++) {
                result[col][row] = matrix[row][col];
            }
        }
        return result;
    }

    static void print(int[][] matrix) {
        for (int[] row : matrix) {
            System.out.println("  " + Arrays.toString(row));
        }
    }

    public static void main(String[] args) {
        int[][] matrix = {{1, 2, 3}, {4, 5, 6}};
        System.out.println("the original has " + matrix.length + " rows:");
        print(matrix);

        int[][] flipped = transpose(matrix);
        System.out.println("the transpose has " + flipped.length + " rows:");
        print(flipped);

        System.out.println("transposing twice returns the original: "
                + Arrays.deepEquals(matrix, transpose(flipped)));
        System.out.println("note deepEquals for nested arrays; equals would compare the row references");
    }
}
