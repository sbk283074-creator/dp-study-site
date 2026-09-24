public class Sol4 {
    static final class Counter {
        private static int instances;
        private final int max;
        private int value;

        Counter(int max) {
            if (max <= 0) {
                throw new IllegalArgumentException("max must be positive: " + max);
            }
            this.max = max;
            instances++;
        }

        static int instances() {
            return instances;
        }

        boolean increment() {
            if (value == max) {
                return false;
            }
            value++;
            return true;
        }

        int value() {
            return value;
        }

        int max() {
            return max;
        }
    }

    public static void main(String[] args) {
        Counter small = new Counter(3);
        Counter tiny = new Counter(1);

        for (int i = 0; i < 5; i++) {
            System.out.println("increment " + i + " on small: " + small.increment()
                    + " (value " + small.value() + " of " + small.max() + ")");
        }

        System.out.println("tiny increments once: " + tiny.increment()
                + ", then refuses: " + tiny.increment());
        System.out.println("the instance count belongs to the class: " + Counter.instances());
    }
}
