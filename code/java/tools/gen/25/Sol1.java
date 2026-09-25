public class Sol1 {
    enum Status {
        OK(200, "OK"),
        CREATED(201, "Created"),
        NO_CONTENT(204, "No Content"),
        NOT_MODIFIED(304, "Not Modified"),
        BAD_REQUEST(400, "Bad Request"),
        NOT_FOUND(404, "Not Found"),
        METHOD_NOT_ALLOWED(405, "Method Not Allowed"),
        INTERNAL_ERROR(500, "Internal Server Error");

        final int code;
        final String reason;

        Status(int code, String reason) {
            this.code = code;
            this.reason = reason;
        }

        String family() {
            return switch (code / 100) {
                case 1 -> "informational";
                case 2 -> "success";
                case 3 -> "redirect";
                case 4 -> "client error";
                case 5 -> "server error";
                default -> "not a status code";
            };
        }

        static Status of(int code) {
            for (Status status : values()) {
                if (status.code == code) {
                    return status;
                }
            }
            throw new IllegalArgumentException("no status " + code);
        }
    }

    public static void main(String[] args) {
        for (Status status : Status.values()) {
            System.out.printf("%-18s %d %-20s %s%n",
                    status.name(), status.code, status.reason, status.family());
        }

        System.out.println();
        System.out.println("Status.of(404)     = " + Status.of(404));
        System.out.println("Status.of(418)     = " + caught(418));
        System.out.println("Status.of(404).family() = " + Status.of(404).family());
        System.out.println();
        System.out.println("the enum closes the set: every status this service can send is one of eight");
    }

    static String caught(int code) {
        try {
            return Status.of(code).toString();
        } catch (IllegalArgumentException e) {
            return "IllegalArgumentException: " + e.getMessage();
        }
    }
}
