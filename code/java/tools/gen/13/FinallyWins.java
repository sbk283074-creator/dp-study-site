public class FinallyWins {

    @SuppressWarnings("finally")
    static int returnFromFinally() {
        try {
            return 1;
        } finally {
            return 2;
        }
    }

    static int reassignInFinally() {
        int result = 1;
        try {
            return result;
        } finally {
            result = 2;
        }
    }

    public static void main(String[] args) {
        System.out.println("a return in finally wins: " + returnFromFinally());
        System.out.println("reassigning the local does not: " + reassignInFinally());
        System.out.println("the return value was already computed: "
                + (reassignInFinally() == 1));
    }
}
