public class Sol2 {
    static int parsePort(String raw) {
        int port = Integer.parseInt(raw);
        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("port out of range: " + port);
        }
        return port;
    }

    static String expectFailure(String raw) {
        try {
            parsePort(raw);
            return "no exception";
        } catch (RuntimeException e) {
            return e.getClass().getSimpleName() + ": " + e.getMessage();
        }
    }

    public static void main(String[] args) {
        System.out.println("ok        = " + parsePort("8080"));
        for (String raw : new String[] {"0", "70000", "http", "-1"}) {
            System.out.printf("%-8s-> %s%n", raw, expectFailure(raw));
        }
    }
}
