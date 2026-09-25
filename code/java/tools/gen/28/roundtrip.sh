cat > RoundTrip.java <<'EOF'
public class RoundTrip {
    public static void main(String[] args) {
        String[] documents = {
            "{}", "[]", "{\"a\":[]}", "[1,2,3]", "{\"a\":{\"b\":[true,false,null]}}",
            "{\"esc\":\"a\\nb\"}", "  {  \"spaced\" :  1  }  ",
        };

        for (String document : documents) {
            Json once = JsonParser.parse(document);
            String written = JsonWriter.write(once);
            String twice = JsonWriter.write(JsonParser.parse(written));
            System.out.printf("%-30s -> %-30s stable=%s%n", document, written,
                    written.equals(twice));
        }

        System.out.println();
        System.out.println("whitespace is not part of the value, so the first write normalises it");
        System.out.println("and the second write is byte-for-byte the same as the first");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out RoundTrip.java
java -cp out RoundTrip
