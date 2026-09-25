public class Sol2 {
    record RequestLine(String method, String target, String version) {
        static RequestLine parse(String line) {
            String[] parts = line.split(" ");
            if (parts.length != 3) {
                throw new IllegalArgumentException(
                        "expected three space-separated parts, found " + parts.length);
            }
            return new RequestLine(parts[0], parts[1], parts[2]);
        }
    }

    public static void main(String[] args) {
        String[] lines = {
            "GET /notes HTTP/1.1",
            "POST /notes?tag=work HTTP/1.1",
            "DELETE /notes/7 HTTP/1.1",
            "GET / HTTP/1.0",
            "GET  /two-spaces HTTP/1.1",
            "GET /notes",
        };

        for (String line : lines) {
            try {
                RequestLine request = RequestLine.parse(line);
                System.out.printf("%-28s -> %s%n", line,
                        request.method() + " " + request.target() + " " + request.version());
            } catch (IllegalArgumentException e) {
                System.out.printf("%-28s -> %s%n", line, e.getMessage());
            }
        }

        System.out.println();
        System.out.println("split(\" \") keeps empty parts, so two spaces make four fields, not three");
        System.out.println("the target is still raw here: splitting off the query is the next step");
    }
}
