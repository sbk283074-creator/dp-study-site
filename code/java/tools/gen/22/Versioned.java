public class Versioned {
    static final String HEADER = "# quill-2";

    static String save(String... bodies) {
        StringBuilder out = new StringBuilder(HEADER).append('\n');
        int id = 1;
        for (String body : bodies) {
            out.append(id++).append('\t').append(body).append('\n');
        }
        return out.toString();
    }

    static int load(String text) {
        String[] lines = text.split("\n", -1);
        if (lines.length == 0 || !lines[0].startsWith("# ")) {
            throw new IllegalArgumentException("not a quill file: no header line");
        }
        String version = lines[0].substring(2);
        if (!version.equals("quill-2")) {
            throw new IllegalArgumentException("unsupported version: " + version);
        }
        int count = 0;
        for (String line : lines) {
            if (!line.isBlank()) {
                count++;
            }
        }
        return count - 1;
    }

    static String show(String s) {
        return "'" + s.replace("\n", "\\n").replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String[] files = {
            save("milk and eggs", "chapter 22"),
            "# quill-1\n1\tmilk\n",
            "1\tmilk\n",
        };

        for (String text : files) {
            try {
                System.out.printf("%-48s -> %d note(s)%n", show(text), load(text));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-48s -> %s%n", show(text), e.getMessage());
            }
        }

        System.out.println();
        System.out.println("a version this build does not understand is refused, not guessed at");
    }
}
