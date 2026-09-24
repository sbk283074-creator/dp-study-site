public class Constructors {
    private final String name;
    private final int limit;
    private final boolean active;

    Constructors(String name) {
        this(name, 10);
    }

    Constructors(String name, int limit) {
        this(name, limit, true);
    }

    Constructors(String name, int limit, boolean active) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank");
        }
        if (limit < 0) {
            throw new IllegalArgumentException("limit must not be negative: " + limit);
        }
        this.name = name;
        this.limit = limit;
        this.active = active;
    }

    @Override
    public String toString() {
        return name + "(limit=" + limit + ", active=" + active + ")";
    }

    public static void main(String[] args) {
        System.out.println("one argument   : " + new Constructors("alpha"));
        System.out.println("two arguments  : " + new Constructors("beta", 25));
        System.out.println("three arguments: " + new Constructors("gamma", 0, false));

        try {
            new Constructors("   ");
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        try {
            new Constructors("delta", -5);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
    }
}
