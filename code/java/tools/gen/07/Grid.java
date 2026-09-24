import java.util.Arrays;

public class Grid {
    public static void main(String[] args) {
        int[][] grid = new int[3][4];
        System.out.println("rows          = " + grid.length);
        System.out.println("columns       = " + grid[0].length);
        System.out.println("grid[0] is an int[] : " + (grid[0] instanceof int[]));

        for (int row = 0; row < grid.length; row++) {
            for (int col = 0; col < grid[row].length; col++) {
                grid[row][col] = (row + 1) * (col + 1);
            }
        }
        for (int[] row : grid) {
            System.out.println("  " + Arrays.toString(row));
        }

        int[][] jagged = {{1}, {2, 3}, {4, 5, 6}};
        System.out.println("a jagged array has rows of different lengths:");
        for (int[] row : jagged) {
            System.out.println("  length " + row.length + " -> " + Arrays.toString(row));
        }
        System.out.println("int[][] is an array of int[], which is why it need not be a rectangle");
    }
}
