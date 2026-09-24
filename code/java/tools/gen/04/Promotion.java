public class Promotion {
    static String type(Object value) {
        return value.getClass().getSimpleName();
    }

    public static void main(String[] args) {
        byte b = 10;
        short s = 20;
        char c = 'A';
        int i = 30;
        long l = 40L;
        float f = 50f;
        double d = 60.0;

        System.out.println("byte  + byte   -> " + type(b + b));
        System.out.println("short + int    -> " + type(s + i));
        System.out.println("char  + char   -> " + type(c + c));
        System.out.println("char  + int    -> " + type(c + i));
        System.out.println("int   + long   -> " + type(i + l));
        System.out.println("long  + float  -> " + type(l + f));
        System.out.println("float + double -> " + type(f + d));

        System.out.println("'A' + 1        = " + (c + 1));
        System.out.println("(char)('A' + 1)= " + (char) (c + 1));

        System.out.println("10 / 4.0       = " + (10 / 4.0));
        System.out.println("1 + 2 + \"x\"    = " + (1 + 2 + "x"));
        System.out.println("\"x\" + 1 + 2    = " + ("x" + 1 + 2));
    }
}
