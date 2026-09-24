public class Hierarchy {

    public static void main(String[] args) {
        Throwable runtime = new RuntimeException("x");
        Throwable error = new OutOfMemoryError("x");
        Throwable checked = new java.io.IOException("x");

        System.out.println("a RuntimeException is an Exception: " + (runtime instanceof Exception));
        System.out.println("an Error is not an Exception: " + !(error instanceof Exception));
        System.out.println("an IOException is an Exception: " + (checked instanceof Exception));
        System.out.println("all three are Throwable: "
                + (runtime instanceof Throwable && error instanceof Throwable
                   && checked instanceof Throwable));

        System.out.println("NumberFormatException is unchecked: "
                + RuntimeException.class.isAssignableFrom(NumberFormatException.class));
        System.out.println("IOException is checked: "
                + !RuntimeException.class.isAssignableFrom(java.io.IOException.class));

        Throwable nested = new IllegalStateException("outer", new java.io.IOException("inner"));
        System.out.println("a Throwable can carry another: "
                + nested.getCause().getClass().getSimpleName());
    }
}
