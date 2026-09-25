import java.nio.charset.StandardCharsets;

public class ResponseDemo {
    public static void main(String[] args) {
        Response[] responses = {
            Response.ok("every note"),
            Response.text(201, "added buy milk"),
            Response.notFound("/notes/9"),
            Response.methodNotAllowed("PUT", "GET, POST"),
        };

        for (Response response : responses) {
            System.out.printf("%d  %-26s %2d byte(s)  %s%n", response.status(),
                    response.contentType(), response.length(), response.body());
        }

        System.out.println();
        String ascii = "hello";
        String accented = "h\u00e9llo";
        System.out.println("'" + ascii + "' is " + ascii.length() + " char(s) and "
                + ascii.getBytes(StandardCharsets.UTF_8).length + " byte(s)");
        System.out.println("'" + accented + "' is " + accented.length() + " char(s) and "
                + accented.getBytes(StandardCharsets.UTF_8).length + " byte(s)");

        Response tall = Response.ok(accented);
        System.out.println();
        System.out.println("Response.ok(\"" + accented + "\").length() = " + tall.length());
        System.out.println("length() counts bytes, because bytes are what the header promises");
        System.out.println("a writer that used String.length() would promise 5 and send 6");
    }
}
