public class Sol4 {
    enum Status {
        DRAFT, PUBLISHED, ARCHIVED;

        static Status parse(String raw) {
            try {
                return valueOf(raw.toUpperCase());
            } catch (IllegalArgumentException e) {
                throw new IllegalArgumentException("unknown status: " + raw);
            }
        }
    }

    public static void main(String[] args) {
        for (String raw : new String[] {"draft", "Published", "ARCHIVED"}) {
            System.out.printf("%-10s -> %s%n", raw, Status.parse(raw));
        }
        try {
            Status.parse("publishd");
        } catch (IllegalArgumentException e) {
            System.out.println("rejected   -> " + e.getMessage());
        }
        System.out.println("states     = " + Status.values().length);
    }
}
