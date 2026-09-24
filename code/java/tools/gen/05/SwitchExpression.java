public class SwitchExpression {
    static String dayKind(int day) {
        return switch (day) {
            case 0, 6 -> "weekend";
            case 5 -> "friday";
            default -> "weekday";
        };
    }

    static int daysIn(int month) {
        return switch (month) {
            case 2 -> 28;
            case 4, 6, 9, 11 -> 30;
            default -> 31;
        };
    }

    static String band(int score) {
        return switch (score / 10) {
            case 9, 10 -> "A";
            case 7, 8 -> "B";
            case 5, 6 -> "C";
            default -> {
                String label = "F";
                yield label + " (retake)";
            }
        };
    }

    public static void main(String[] args) {
        for (int day = 0; day <= 6; day++) {
            System.out.println("day " + day + " -> " + dayKind(day));
        }
        System.out.println("days in month 2  = " + daysIn(2));
        System.out.println("days in month 4  = " + daysIn(4));
        System.out.println("days in month 12 = " + daysIn(12));

        for (int score : new int[]{95, 75, 42}) {
            System.out.println("score " + score + " -> " + band(score));
        }
    }
}
