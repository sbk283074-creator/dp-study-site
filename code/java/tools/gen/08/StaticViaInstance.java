public class StaticViaInstance {
    static int created;

    public static void main(String[] args) {
        StaticViaInstance instance = new StaticViaInstance();
        System.out.println(instance.created);
    }
}
