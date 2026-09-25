public class ThrowParse {
    public static void main(String[] args) {
        System.out.println("about to parse");
        int id = Integer.parseInt("abc");
        System.out.println("never printed: " + id);
    }
}
