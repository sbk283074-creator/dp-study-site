public class EnumSwitch {
    enum Level { LOW, MEDIUM, HIGH }

    static int threshold(Level level) {
        return switch (level) {
            case LOW -> 10;
            case MEDIUM -> 50;
            case HIGH -> 90;
        };
    }

    static String note(Level level) {
        return switch (level) {
            case LOW, MEDIUM -> "routine";
            case HIGH -> "escalate";
        };
    }

    public static void main(String[] args) {
        for (Level level : Level.values()) {
            System.out.printf("%-7s threshold=%-3d note=%s%n",
                    level, threshold(level), note(level));
        }
    }
}
