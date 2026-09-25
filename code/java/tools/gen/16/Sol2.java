public class Sol2 {
    enum Op {
        PLUS("+") {
            int apply(int a, int b) {
                return a + b;
            }
        },
        MINUS("-") {
            int apply(int a, int b) {
                return a - b;
            }
        },
        TIMES("*") {
            int apply(int a, int b) {
                return a * b;
            }
        };

        private final String symbol;

        Op(String symbol) {
            this.symbol = symbol;
        }

        abstract int apply(int a, int b);

        String symbol() {
            return symbol;
        }
    }

    public static void main(String[] args) {
        for (Op op : Op.values()) {
            System.out.printf("3 %s 4 = %d%n", op.symbol(), op.apply(3, 4));
        }
        System.out.println("count  = " + Op.values().length);
    }
}
