cat > Scenario.java <<'JAVA'
public class Scenario {
    public static void main(String[] args) {
        Suite suite = new Suite();

        suite.add("the bug that is already fixed", a -> {
            a.equal("a &amp; b", Escaping.html("a & b"), "escaping works");
            a.equal(2, 1 + 1, "arithmetic works");
        });

        suite.add("the bug nobody wrote a test for", a -> {
            String once = Escaping.html("a & b");
            a.equal("a &amp; b", once, "escaped once");
            a.equal("a &amp; b", Escaping.html(once), "escaped twice, which is wrong");
        });

        int failed = suite.run();
        System.out.println();
        System.out.println(failed + " failure(s) is the number the build should care about.");
        System.out.println("The second test is the one that earns its keep: it encodes a");
        System.out.println("decision (\"escape at the last moment, once\") rather than a");
        System.out.println("behaviour the code already happens to have");
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Scenario.java
java -cp out Scenario
