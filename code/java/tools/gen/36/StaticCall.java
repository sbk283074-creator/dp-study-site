public class StaticCall {
    public static void main(String[] args) {
        StaticCall instance = new StaticCall();
        System.out.println(instance.describe());
    }

    public static String describe() {
        return "a static method reached through an instance";
    }
}
