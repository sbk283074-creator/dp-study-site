public class StackOverflow {
    static int descend(int depth) {
        return descend(depth + 1) + 1;
    }

    public static void main(String[] args) {
        System.out.println(descend(0));
    }
}
