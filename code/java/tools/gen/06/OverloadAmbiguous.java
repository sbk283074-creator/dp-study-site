public class OverloadAmbiguous {
    static String pick(int a, long b) {
        return "int, long";
    }

    static String pick(long a, int b) {
        return "long, int";
    }

    public static void main(String[] args) {
        System.out.println(pick(1, 2));
    }
}
