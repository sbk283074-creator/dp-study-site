public class SwitchStatement {
    static String dayKind(int day) {
        String kind;
        switch (day) {
            case 0:
            case 6:
                kind = "weekend";
                break;
            case 5:
                kind = "friday";
                break;
            default:
                kind = "weekday";
                break;
        }
        return kind;
    }

    public static void main(String[] args) {
        for (int day = 0; day <= 6; day++) {
            System.out.println("day " + day + " -> " + dayKind(day));
        }

        String role = "admin";
        switch (role) {
            case "admin":
                System.out.println("a switch also selects on a String");
                break;
            default:
                System.out.println("limited access");
                break;
        }
    }
}
