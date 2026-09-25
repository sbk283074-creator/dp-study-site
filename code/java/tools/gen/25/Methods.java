public class Methods {
    record Method(String name, boolean safe, boolean idempotent, boolean typicalBody) {}

    public static void main(String[] args) {
        Method[] methods = {
            new Method("GET", true, true, false),
            new Method("HEAD", true, true, false),
            new Method("PUT", false, true, true),
            new Method("DELETE", false, true, false),
            new Method("POST", false, false, true),
            new Method("PATCH", false, false, true),
        };

        System.out.printf("%-8s %-7s %-12s %s%n", "method", "safe", "idempotent", "request body");
        for (Method method : methods) {
            System.out.printf("%-8s %-7b %-12b %b%n", method.name(), method.safe(),
                    method.idempotent(), method.typicalBody());
        }
        System.out.println();
        System.out.println("safe: no side effects. idempotent: doing it twice has the same effect as once");
        System.out.println("POST is neither, and that is why a browser asks before resending one");
    }
}
