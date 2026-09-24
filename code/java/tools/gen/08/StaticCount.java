public class StaticCount {
    static int created;
    final int serial;

    StaticCount() {
        created++;
        serial = created;
    }

    static int created() {
        return created;
    }

    @Override
    public String toString() {
        return "instance " + serial;
    }

    public static void main(String[] args) {
        System.out.println("before any instance: created = " + StaticCount.created());

        StaticCount first = new StaticCount();
        StaticCount second = new StaticCount();
        StaticCount third = new StaticCount();

        System.out.println(first + ", " + second + ", " + third);
        System.out.println("after three: created = " + StaticCount.created());
        System.out.println("the serials add to " + (first.serial + second.serial + third.serial));
        System.out.println("one field is per class and one is per object");
    }
}
