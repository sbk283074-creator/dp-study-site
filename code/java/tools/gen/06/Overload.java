public class Overload {
    static String pick(int value) {
        return "int";
    }

    static String pick(long value) {
        return "long";
    }

    static String pick(double value) {
        return "double";
    }

    static String pick(Integer value) {
        return "Integer";
    }

    static String pick(Object value) {
        return "Object";
    }

    static String pick(int a, int b) {
        return "two ints";
    }

    public static void main(String[] args) {
        byte small = 1;
        short medium = 2;
        char letter = 'x';
        Integer boxed = 5;

        System.out.println("pick(1)      -> " + pick(1));
        System.out.println("pick(1L)     -> " + pick(1L));
        System.out.println("pick(1.0)    -> " + pick(1.0));
        System.out.println("pick(1.0f)   -> " + pick(1.0f));
        System.out.println("pick(boxed)  -> " + pick(boxed));
        System.out.println("pick(\"text\") -> " + pick("text"));
        System.out.println("pick(byte)   -> " + pick(small));
        System.out.println("pick(short)  -> " + pick(medium));
        System.out.println("pick(char)   -> " + pick(letter));
        System.out.println("pick(1, 2)   -> " + pick(1, 2));
    }
}
