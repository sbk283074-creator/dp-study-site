public class Fallthrough {
    static String describe(int level) {
        String result = "";
        switch (level) {
            case 3:
                result += "admin ";
            case 2:
                result += "write ";
            case 1:
                result += "read";
                break;
            default:
                result = "none";
        }
        return result;
    }

    public static void main(String[] args) {
        for (int level = 0; level <= 3; level++) {
            System.out.println("level " + level + " -> " + describe(level));
        }
    }
}
