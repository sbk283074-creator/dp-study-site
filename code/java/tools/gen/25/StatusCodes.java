public class StatusCodes {
    record Status(int code, String reason) {}

    static String family(int code) {
        return switch (code / 100) {
            case 1 -> "informational";
            case 2 -> "success";
            case 3 -> "redirect";
            case 4 -> "client error";
            case 5 -> "server error";
            default -> "not a status code";
        };
    }

    public static void main(String[] args) {
        Status[] table = {
            new Status(200, "OK"),
            new Status(201, "Created"),
            new Status(204, "No Content"),
            new Status(301, "Moved Permanently"),
            new Status(304, "Not Modified"),
            new Status(400, "Bad Request"),
            new Status(401, "Unauthorized"),
            new Status(404, "Not Found"),
            new Status(405, "Method Not Allowed"),
            new Status(500, "Internal Server Error"),
            new Status(503, "Service Unavailable"),
        };

        System.out.printf("%-5s %-22s %s%n", "code", "reason", "family");
        for (Status status : table) {
            System.out.printf("%-5d %-22s %s%n",
                    status.code(), status.reason(), family(status.code()));
        }
        System.out.println();
        System.out.println("the first digit is the family, and the family is what a client acts on");
    }
}
