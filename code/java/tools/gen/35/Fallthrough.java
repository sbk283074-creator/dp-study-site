public class Fallthrough {
    public static void main(String[] args) {
        int code = 1;
        switch (code) {
            case 1:
                System.out.println("one");
            case 2:
                System.out.println("two");
                break;
            default:
                break;
        }
    }
}
