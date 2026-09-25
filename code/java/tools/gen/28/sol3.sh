cat > Sol3.java <<'EOF'
import java.math.BigDecimal;

public class Sol3 {
    public static void main(String[] args) {
        String body = "{\"price\":0.1,\"tax\":0.2}";
        Json.Obj parsed = (Json.Obj) JsonParser.parse(body);

        BigDecimal price = new BigDecimal(((Json.Num) parsed.get("price")).raw());
        BigDecimal tax = new BigDecimal(((Json.Num) parsed.get("tax")).raw());
        System.out.println("from the raw text: " + price.add(tax));

        double priceAsDouble = ((Json.Num) parsed.get("price")).asDouble();
        double taxAsDouble = ((Json.Num) parsed.get("tax")).asDouble();
        System.out.println("from the doubles:  " + (priceAsDouble + taxAsDouble));

        System.out.println();
        System.out.println("both answers came out of the same body, and only one of them is money");
        System.out.println("BigDecimal can only be built from the text, which is why the parser kept it");
    }
}
EOF

javac -Xlint:all -Werror -cp out -d out Sol3.java
java -cp out Sol3
