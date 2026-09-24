public class TryCatch {

    static final StringBuilder trace = new StringBuilder();

    static void step(String label) {
        trace.append(label).append(' ');
    }

    static void run() {
        try {
            step("try");
            throw new IllegalStateException("boom");
        } catch (IllegalStateException e) {
            step("catch");
        } finally {
            step("finally");
        }
        step("after");
    }

    public static void main(String[] args) {
        run();
        System.out.println("order: " + trace.toString().trim());
        System.out.println("finally runs on the way out either way");
    }
}
