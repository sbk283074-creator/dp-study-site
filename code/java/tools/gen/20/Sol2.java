public class Sol2 {
    record SafeNote(int id, String title, String body) {
        SafeNote {
            if (title.indexOf('\t') >= 0 || title.indexOf('\n') >= 0) {
                throw new IllegalArgumentException("tab or newline in title");
            }
        }

        String render() {
            return id + "\t" + title + "\t" + body;
        }

        static SafeNote parse(String line) {
            String[] parts = line.split("\t", 3);
            if (parts.length != 3) {
                throw new IllegalArgumentException("not a note line");
            }
            return new SafeNote(Integer.parseInt(parts[0]), parts[1], parts[2]);
        }
    }

    static String show(String s) {
        return "'" + s.replace("\t", "\\t").replace("\n", "\\n") + "'";
    }

    public static void main(String[] args) {
        String[] titles = {"Groceries", "Groceries\tand more", "Two\nlines", "", "Ünïcode"};

        int accepted = 0;
        int lossless = 0;
        for (String title : titles) {
            try {
                SafeNote note = new SafeNote(1, title, "milk\tand eggs");
                accepted++;
                if (SafeNote.parse(note.render()).equals(note)) {
                    lossless++;
                }
                System.out.printf("%-22s accepted%n", show(title));
            } catch (IllegalArgumentException e) {
                System.out.printf("%-22s rejected%n", show(title));
            }
        }

        System.out.println();
        System.out.println("accepted " + accepted + " of " + titles.length);
        System.out.println("round-tripped losslessly " + lossless + " of " + accepted);
    }
}
