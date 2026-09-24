public class Sol5 {
    public static void main(String[] args) {
        int[] scores = {7, 8, 9, 10, 12};
        int total = 0;
        for (int score : scores) {
            total += score;
        }

        double naive = total / scores.length;
        double correct = (double) total / scores.length;

        System.out.println("total            = " + total);
        System.out.println("count            = " + scores.length);
        System.out.println("total / count    = " + (total / scores.length));
        System.out.println("double naive     = " + naive);
        System.out.println("double correct   = " + correct);
        System.out.println("naive lost       = " + (correct - naive));
    }
}
