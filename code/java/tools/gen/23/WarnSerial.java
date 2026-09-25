public class WarnSerial {
    static class UsageException extends RuntimeException {
        UsageException(String message) {
            super(message);
        }
    }

    public static void main(String[] args) {
        System.out.println(new UsageException("missing argument").getMessage());
    }
}
