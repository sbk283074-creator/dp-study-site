public class BadRecord {
    record Bad(int x) {
        private int cache;
    }

    public static void main(String[] args) {
        System.out.println(new Bad(1));
    }
}
