cat > Sol2.java <<'EOF'
public class Sol2 {
    static int occurrences(String text, String needle) {
        int count = 0;
        int at = text.indexOf(needle);
        while (at >= 0) {
            count++;
            at = text.indexOf(needle, at + needle.length());
        }
        return count;
    }

    public static void main(String[] args) {
        String body = "{\"role\":\"user\",\"role\":\"admin\"}";
        Json.Obj parsed = (Json.Obj) JsonParser.parse(body);

        System.out.println("the body:                   " + body);
        System.out.println("members named 'role' in it: " + occurrences(body, "\"role\""));
        System.out.println("members named 'role' out:   " + parsed.members().size());
        System.out.println("the value kept:             " + ((Json.Str) parsed.get("role")).value());

        System.out.println();
        System.out.println("two went in and one came out, and nothing said so");
        System.out.println("a proxy that keeps the first and a service that keeps the last disagree");
        System.out.println("about a body they both call valid, so a duplicate name is worth rejecting");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol2.java
java -cp out Sol2
