public class SwitchExhaustive {
    static String name(int day) {
        return switch (day) {
            case 0 -> "sunday";
            case 1 -> "monday";
        };
    }

    public static void main(String[] args) {
        System.out.println(name(0));
    }
}
