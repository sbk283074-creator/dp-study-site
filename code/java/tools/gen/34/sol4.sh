cat > Sol4.java <<'JAVA'
public class Sol4 {
    public static void main(String[] args) {
        String stored = "0123456789abcdef";
        String guessEarly = "x123456789abcdef";
        String guessLate = "0123456789abcdex";

        System.out.println("String.equals, first char wrong : compared "
                + Secrets.countEquals(stored, guessEarly));
        System.out.println("String.equals, last char wrong  : compared "
                + Secrets.countEquals(stored, guessLate));

        Secrets.equalsAlways(stored, guessEarly);
        int early = Secrets.compared;
        Secrets.equalsAlways(stored, guessLate);
        int late = Secrets.compared;
        System.out.println("equal-time, first char wrong    : compared " + early);
        System.out.println("equal-time, last char wrong     : compared " + late);
        System.out.println();
        System.out.println("the first two numbers differ, and that difference is measurable");
        System.out.println("from across a network. The second two are the same, so there is");
        System.out.println("nothing to measure");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol4.java
java -cp out Sol4
