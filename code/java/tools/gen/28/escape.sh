cat > Escape.java <<'EOF'
public class Escape {
    /** Renders a string so a control character is visible in the transcript. */
    static String visible(String text) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c < 0x20 || c == '\u2028' || c == '\u2029') {
                String hex = Integer.toHexString(c);
                out.append("\\u").append("0000".substring(hex.length())).append(hex);
            } else {
                out.append(c);
            }
        }
        return out.toString();
    }

    public static void main(String[] args) {
        String[] samples = {
            "plain", "a\"b", "a\\b", "line\nbreak", "tab\there",
            "nul\u0001here", "caf\u00e9", "slash/here", "sep\u2028here",
        };

        boolean all = true;
        for (String sample : samples) {
            String written = JsonWriter.write(new Json.Str(sample));
            String back = ((Json.Str) JsonParser.parse(written)).value();
            all = all && back.equals(sample);
            System.out.printf("%-16s -> %s%n", visible(sample), written);
        }

        System.out.println();
        System.out.println("all " + samples.length + " came back unchanged: " + all);
        System.out.println();
        System.out.println("the reader accepts \\/ and the writer never emits it:");
        System.out.println("  a\\/b -> " + ((Json.Str) JsonParser.parse("\"a\\/b\"")).value());
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Escape.java
java -cp out Escape
