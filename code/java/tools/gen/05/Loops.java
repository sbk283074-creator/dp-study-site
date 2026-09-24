public class Loops {
    public static void main(String[] args) {
        System.out.print("for      :");
        for (int i = 0; i < 5; i++) {
            System.out.print(" " + i);
        }
        System.out.println();

        System.out.print("while    :");
        int n = 0;
        while (n < 5) {
            System.out.print(" " + n);
            n++;
        }
        System.out.println();

        System.out.print("do-while :");
        int m = 10;
        do {
            System.out.print(" " + m);
            m++;
        } while (m < 5);
        System.out.println();

        System.out.print("continue :");
        for (int i = 0; i < 10; i++) {
            if (i % 2 == 0) {
                continue;
            }
            System.out.print(" " + i);
        }
        System.out.println();

        System.out.print("break    :");
        for (int i = 0; i < 100; i++) {
            if (i == 3) {
                break;
            }
            System.out.print(" " + i);
        }
        System.out.println();

        System.out.println("labelled break leaves both loops at once:");
        outer:
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                if (row * 3 + col == 4) {
                    System.out.println("  stopped at row " + row + ", col " + col);
                    break outer;
                }
            }
        }

        int declaredOutside = 0;
        for (; declaredOutside < 3; declaredOutside++) {
            // counting only; the loop variable lives outside the loop
        }
        System.out.println("declared outside, still in scope: " + declaredOutside);
    }
}
