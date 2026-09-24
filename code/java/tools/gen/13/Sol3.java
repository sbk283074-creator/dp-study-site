public class Sol3 {

    static final class ConfigException extends Exception {
        private static final long serialVersionUID = 1L;

        private final String key;

        ConfigException(String key, String problem, Throwable cause) {
            super("config key '" + key + "': " + problem, cause);
            this.key = key;
        }

        String key() {
            return key;
        }
    }

    static int readPort(String raw) throws ConfigException {
        try {
            int port = Integer.parseInt(raw);
            if (port < 1 || port > 65535) {
                throw new ConfigException("port", "out of range: " + port, null);
            }
            return port;
        } catch (NumberFormatException e) {
            throw new ConfigException("port", "not a number: " + raw, e);
        }
    }

    public static void main(String[] args) {
        for (String raw : new String[]{"8080", "abc", "99999"}) {
            try {
                System.out.println(raw + " -> " + readPort(raw));
            } catch (ConfigException e) {
                String cause = e.getCause() == null
                        ? "none" : e.getCause().getClass().getSimpleName();
                System.out.println(raw + " -> " + e.getMessage() + " (cause: " + cause + ")");
                System.out.println("   key carried as data: " + e.key());
            }
        }
    }
}
