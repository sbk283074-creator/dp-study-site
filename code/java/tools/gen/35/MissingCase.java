public class MissingCase {
    enum Level { DEBUG, INFO, WARN, ERROR }

    public static void main(String[] args) {
        Level level = Level.WARN;
        String shortName = switch (level) {
            case DEBUG -> "D";
            case INFO -> "I";
        };
        System.out.println(shortName);
    }
}
