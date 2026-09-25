import java.math.BigDecimal;

public class BadOperator {
    public static void main(String[] args) {
        BigDecimal total = new BigDecimal("10.00");
        System.out.println(total + 1);
    }
}
