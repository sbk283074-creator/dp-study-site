public class Sol1 {
    static String slug(String title) {
        return title.toLowerCase()
                .replaceAll("[^a-z0-9]+", "-")
                .replaceAll("(^-|-$)", "");
    }

    public static void main(String[] args) {
        String[][] cases = {
            {"Hello World", "hello-world"},
            {"  Spaced  Out  ", "spaced-out"},
            {"Already-slugged", "already-slugged"},
            {"Punctuation! Here?", "punctuation-here"},
            {"", ""},
        };

        int passed = 0;
        for (String[] c : cases) {
            String actual = slug(c[0]);
            boolean ok = actual.equals(c[1]);
            if (ok) {
                passed++;
            }
            System.out.printf("%-4s %s%n", ok ? "PASS" : "FAIL",
                    "'" + c[0] + "' -> '" + actual + "'");
        }
        System.out.println("passed " + passed + " of " + cases.length);
    }
}
