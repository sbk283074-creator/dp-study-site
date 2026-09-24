public class Scenario {
    static int totalBytesInt(int[] responses) {
        int total = 0;
        for (int bytes : responses) {
            total += bytes;
        }
        return total;
    }

    static long totalBytesLong(int[] responses) {
        long total = 0;
        for (int bytes : responses) {
            total += bytes;
        }
        return total;
    }

    public static void main(String[] args) {
        int[] responses = {1_500_000_000, 1_000_000_000, 500_000_000};

        int broken = totalBytesInt(responses);
        long correct = totalBytesLong(responses);

        System.out.println("int  total = " + broken + " bytes");
        System.out.println("long total = " + correct + " bytes");
        System.out.println("the int total is negative: " + (broken < 0));

        System.out.println("dashboard shows = " + (broken / 1_073_741_824L) + " GB");
        System.out.println("the truth is    = " + (correct / 1_073_741_824L) + " GB");

        System.out.println("off by exactly 2^32: " + (correct - broken == 4_294_967_296L));
    }
}
