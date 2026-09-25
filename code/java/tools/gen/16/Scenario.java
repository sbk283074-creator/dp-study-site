import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public class Scenario {
    enum Tier { BASIC, PRO, ENTERPRISE }

    sealed interface Discount permits Percent, Flat, None {}
    record Percent(int pct) implements Discount {}
    record Flat(int cents) implements Discount {}
    record None() implements Discount {}

    record Order(String id, Tier tier, int units) {}

    static int priceCents(Order order, Discount discount) {
        int gross = order.units() * 1000;
        return switch (discount) {
            case Percent(int pct) -> gross - gross * pct / 100;
            case Flat(int cents) -> Math.max(0, gross - cents);
            case None() -> gross;
        };
    }

    public static void main(String[] args) {
        List<Order> orders = List.of(
                new Order("A1", Tier.BASIC, 2),
                new Order("A2", Tier.PRO, 5),
                new Order("A3", Tier.PRO, 1),
                new Order("A4", Tier.ENTERPRISE, 10));

        Map<Tier, Discount> policy = new EnumMap<>(Tier.class);
        policy.put(Tier.BASIC, new None());
        policy.put(Tier.PRO, new Percent(10));
        policy.put(Tier.ENTERPRISE, new Flat(2000));

        Map<Tier, Integer> byTier = new EnumMap<>(Tier.class);
        int total = 0;
        for (Order o : orders) {
            int cents = priceCents(o, policy.get(o.tier()));
            total += cents;
            byTier.merge(o.tier(), cents, Integer::sum);
            System.out.printf("%-3s %-11s %6d%n", o.id(), o.tier(), cents);
        }
        System.out.println("by tier = " + byTier);
        System.out.println("total   = " + total);
    }
}
