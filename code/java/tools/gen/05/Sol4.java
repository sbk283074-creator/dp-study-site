public class Sol4 {
    static int discountPercent(int tier) {
        return switch (tier) {
            case 3 -> 20;
            case 2 -> 10;
            case 1 -> 5;
            default -> 0;
        };
    }

    static int priceAfterDiscount(int price, int tier) {
        return price - price * discountPercent(tier) / 100;
    }

    public static void main(String[] args) {
        int price = 10_000;
        int total = 0;
        for (int tier = 0; tier <= 3; tier++) {
            int paid = priceAfterDiscount(price, tier);
            total += paid;
            System.out.println("tier " + tier + ": " + discountPercent(tier) + "% off, pays " + paid);
        }
        System.out.println("four customers together pay " + total);
        System.out.println("with no discount at all they would pay " + (4 * price));
        System.out.println("the discount is monotone in the tier: "
                + (priceAfterDiscount(price, 3) <= priceAfterDiscount(price, 2)
                   && priceAfterDiscount(price, 2) <= priceAfterDiscount(price, 1)));
    }
}
