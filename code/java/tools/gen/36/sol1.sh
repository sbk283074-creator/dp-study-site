cat > Sol1.java <<'JAVA'
public class Sol1 {
    public static void main(String[] args) {
        Suite suite = new Suite();
        suite.add("an empty string survives", a -> {
            a.equal("", Escaping.html(""), "empty in, empty out");
            a.equal("&#39;", Escaping.html("'"), "an apostrophe is escaped");
        });
        suite.add("a value with every character", a -> {
            String all = "<&\"'>";
            a.equal("&lt;&amp;&quot;&#39;&gt;", Escaping.html(all), "all five, in order");
        });
        suite.run();
    }
}
JAVA

javac -Xlint:all -Werror -cp out -d out Sol1.java
java -cp out Sol1
