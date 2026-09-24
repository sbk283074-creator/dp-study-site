public class CallStack {
    static void enter(int n) {
        int local = n * 10;
        System.out.println("enter " + n + "   local = " + local);
        if (n > 0) {
            enter(n - 1);
        }
        System.out.println("leave " + n + "   local still " + local);
    }

    public static void main(String[] args) {
        enter(3);
        System.out.println("leave order is the reverse of enter order: each frame waits for the one below");
    }
}
