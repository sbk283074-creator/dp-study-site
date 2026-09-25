import java.nio.file.Path;

public class PathsDemo {
    public static void main(String[] args) {
        Path p = Path.of("docs", "notes", "todo.txt");

        System.out.println("path       = " + p);
        System.out.println("fileName   = " + p.getFileName());
        System.out.println("parent     = " + p.getParent());
        System.out.println("nameCount  = " + p.getNameCount());
        System.out.println("root       = " + p.getRoot());
        System.out.println("absolute   = " + p.isAbsolute());
        System.out.println("normalised = " + Path.of("a/b/../c").normalize());
        System.out.println("resolved   = " + Path.of("docs").resolve("notes"));
        System.out.println("sibling    = " + Path.of("docs/notes").resolveSibling("archive"));
        System.out.println("relativize = " + Path.of("/a/b/c").relativize(Path.of("/a/d")));
        System.out.println("startsWith = " + p.startsWith("docs"));
    }
}
