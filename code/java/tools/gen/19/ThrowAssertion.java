public class ThrowAssertion {
    static class AssertionFailure extends RuntimeException {
        private static final long serialVersionUID = 1L;

        AssertionFailure(String message) {
            super(message);
        }
    }

    static void assertEquals(int expected, int actual) {
        if (expected != actual) {
            throw new AssertionFailure("expected <" + expected + "> but was <" + actual + ">");
        }
    }

    public static void main(String[] args) {
        assertEquals(4, 2 + 2);
        System.out.println("first assertion held");
        assertEquals(5, 2 + 2);
        System.out.println("this line is never reached");
    }
}
