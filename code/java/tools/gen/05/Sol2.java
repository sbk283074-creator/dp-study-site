public class Sol2 {
    static String triangle(int a, int b, int c) {
        if (a <= 0 || b <= 0 || c <= 0) {
            return "not a triangle";
        }
        if (a + b <= c || b + c <= a || a + c <= b) {
            return "degenerate";
        }
        if (a == b && b == c) {
            return "equilateral";
        }
        if (a == b || b == c || a == c) {
            return "isosceles";
        }
        return "scalene";
    }

    public static void main(String[] args) {
        int[][] cases = {{3, 3, 3}, {3, 3, 5}, {3, 4, 5}, {1, 2, 3}, {0, 1, 1}};
        for (int[] sides : cases) {
            System.out.println(sides[0] + "," + sides[1] + "," + sides[2]
                    + " -> " + triangle(sides[0], sides[1], sides[2]));
        }
        int longest = 5;
        System.out.println("the ternary picks a label: "
                + (longest > 4 ? "long side" : "short side"));
    }
}
