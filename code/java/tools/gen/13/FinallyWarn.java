public class FinallyWarn {

    static int returnFromFinally() {
        try {
            return 1;
        } finally {
            return 2;
        }
    }

    public static void main(String[] args) {
        System.out.println(returnFromFinally());
    }
}
