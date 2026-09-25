public class Sol3 {
    static int parseId(String raw) {
        int id;
        try {
            id = Integer.parseInt(raw);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("'" + raw + "' is not an id");
        }
        if (id <= 0) {
            throw new IllegalArgumentException("ids start at 1, not " + id);
        }
        return id;
    }

    public static void main(String[] args) {
        String[] inputs = {"3", "007", "+3", "0", "-1", " 3", "3 ", "", "abc", "2147483648"};

        for (String raw : inputs) {
            try {
                System.out.printf("%-14s -> %d%n", "'" + raw + "'", parseId(raw));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-14s -> %s%n", "'" + raw + "'", e.getMessage());
            }
        }
    }
}
