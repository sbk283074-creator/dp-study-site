say() {
  printf '%s\n' "$1"
}

cat > Driver.java <<'JAVA'
public class Driver {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader in =
                new java.io.BufferedReader(new java.io.StringReader(""));
        java.io.PrintStream sink =
                new java.io.PrintStream(new java.io.ByteArrayOutputStream());
        String[] argv = {"--vault", "demo", "show", "7"};

        if (args[0].equals("main")) {
            Main.main(argv);
            System.out.println("main returned");
        } else {
            int code = Main.run(argv, in, sink, sink);
            System.out.println("run returned " + code);
            System.out.println("so the next case in the table still runs");
        }
    }
}
JAVA

javac -cp out -d out Driver.java

say '$ java -cp out Driver main'
java -cp out Driver main 2>&1
echo "  -> exit $?"
echo
say '$ java -cp out Driver run'
java -cp out Driver run 2>&1
echo "  -> exit $?"
