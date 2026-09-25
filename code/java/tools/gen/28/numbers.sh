cat > Numbers.java <<'EOF'
public class Numbers {
    public static void main(String[] args) {
        String[] texts = {"1", "1.0", "1e3", "-0", "0.1", "9007199254740993",
                          "12345678901234567890"};

        System.out.printf("%-22s %-22s %-22s %s%n", "text", "raw kept", "as a double", "same?");
        for (String text : texts) {
            Json.Num number = (Json.Num) JsonParser.parse(text);
            String asDouble = String.valueOf(number.asDouble());
            System.out.printf("%-22s %-22s %-22s %s%n", text, number.raw(), asDouble,
                    number.raw().equals(asDouble) ? "yes" : "no");
        }

        System.out.println();
        System.out.println("9007199254740993 is 2^53 + 1, the first integer a double cannot hold:");
        Json.Num big = (Json.Num) JsonParser.parse("9007199254740993");
        System.out.println("  as a long    : " + big.asLong());
        System.out.println("  as a double  : " + (long) big.asDouble());
        System.out.println("  written back : " + JsonWriter.write(big));
        System.out.println();
        System.out.println("a parser that stored a double would write 9007199254740992 back,");
        System.out.println("with no error anywhere, so the text is what this parser keeps");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Numbers.java
java -cp out Numbers
