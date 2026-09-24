public class MissingSerial {

    static final class ConfigException extends Exception {
        ConfigException(String message) {
            super(message);
        }
    }

    public static void main(String[] args) throws ConfigException {
        throw new ConfigException("bad config");
    }
}
