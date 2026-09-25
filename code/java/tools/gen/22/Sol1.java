public class Sol1 {
    static String show(String s) {
        return "'" + s.replace("\\", "\\\\").replace("\n", "\\n")
                .replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String[] titles = {"Groceries", "Groceries\tand more", "Two\nlines", "back\\slash"};

        int ok = 0;
        for (String title : titles) {
            Note note = new Note(1, title, "milk and eggs");
            Note back = Note.parse(note.render());
            boolean same = back.equals(note);
            if (same) {
                ok++;
            }
            System.out.printf("%-24s stored %-32s %s%n",
                    show(title), show(note.render()), same ? "ok" : "LOST");
        }

        System.out.println();
        System.out.println("round-tripped " + ok + " of " + titles.length);
        System.out.println("chapter 20 had to reject the second title; the format now holds it");
    }
}
