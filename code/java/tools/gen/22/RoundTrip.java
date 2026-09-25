public class RoundTrip {
    static String show(String s) {
        return "'" + s.replace("\\", "\\\\").replace("\n", "\\n")
                .replace("\t", "\\t").replace("\r", "\\r") + "'";
    }

    public static void main(String[] args) {
        String[] nasty = {
            "",
            "plain",
            "two\nlines",
            "a\tb",
            "back\\slash",
            "already \\n escaped",
            "\\",
            "\r\n",
            "trailing space ",
        };

        int passed = 0;
        for (String field : nasty) {
            Note note = new Note(1, field, field);
            String stored = note.render();
            Note back = Note.parse(stored);
            boolean same = back.equals(note);
            if (same) {
                passed++;
            }
            System.out.printf("%-24s stored %-34s %s%n",
                    show(field), show(stored), same ? "ok" : "LOST");
        }

        System.out.println();
        System.out.println("round-tripped " + passed + " of " + nasty.length);
    }
}
