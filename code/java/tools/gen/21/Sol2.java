public class Sol2 {
    static int parseId(String raw) {
        try {
            return Integer.parseInt(raw);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("not a note id: '" + raw + "'");
        }
    }

    public static void main(String[] args) {
        String[] inputs = {"7", "+7", "007", " 7", "7 ", "", "abc", "999999999999"};

        int accepted = 0;
        for (String raw : inputs) {
            try {
                int id = parseId(raw);
                accepted++;
                System.out.printf("%-16s -> %d%n", "'" + raw + "'", id);
            } catch (IllegalArgumentException e) {
                System.out.printf("%-16s -> rejected: %s%n", "'" + raw + "'", e.getMessage());
            }
        }

        System.out.println();
        System.out.println("accepted " + accepted + " of " + inputs.length);
    }
}
