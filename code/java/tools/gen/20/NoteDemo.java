public class NoteDemo {
    static String show(String s) {
        return s.replace("\t", "\\t");
    }

    public static void main(String[] args) {
        Note original = new Note(1, "Groceries", "milk\teggs");
        String line = original.render();
        Note reread = Note.parse(line);

        System.out.println("line        = " + show(line));
        System.out.println("round trip  = " + reread.equals(original));
        System.out.println("body        = " + show(reread.body()));

        System.out.println();

        Note awkward = new Note(2, "A\tB", "x");
        Note damaged = Note.parse(awkward.render());
        System.out.println("title in    = " + show(awkward.title()));
        System.out.println("title out   = " + damaged.title());
        System.out.println("body out    = " + show(damaged.body()));
    }
}
