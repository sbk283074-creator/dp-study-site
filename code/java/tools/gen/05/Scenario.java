public class Scenario {
    /**
     * Every case assigns, and only the last one breaks -- so the last
     * assignment wins and the highest tier gets the smallest discount.
     */
    @SuppressWarnings("fallthrough")
    static int discountPercentStatement(int tier) {
        int percent = 0;
        switch (tier) {
            case 3:
                percent = 20;
            case 2:
                percent = 10;
            case 1:
                percent = 5;
                break;
            default:
                percent = 0;
        }
        return percent;
    }

    static int discountPercentExpression(int tier) {
        return switch (tier) {
            case 3 -> 20;
            case 2 -> 10;
            case 1 -> 5;
            default -> 0;
        };
    }

    public static void main(String[] args) {
        int price = 10_000;
        for (int tier = 0; tier <= 3; tier++) {
            System.out.println("tier " + tier
                    + ": the statement gives " + discountPercentStatement(tier) + "%"
                    + ", the expression gives " + discountPercentExpression(tier) + "%");
        }

        int paid = price - price * discountPercentStatement(3) / 100;
        int owed = price - price * discountPercentExpression(3) / 100;
        System.out.println("tier 3 pays " + paid + " and should have paid " + owed);
        System.out.println("undercharged by " + (paid - owed));
    }
}
