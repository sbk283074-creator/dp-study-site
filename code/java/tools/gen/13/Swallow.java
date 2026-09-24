public class Swallow {

    static int parse(String text) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    public static void main(String[] args) {
        System.out.println("parse(\"42\"): " + parse("42"));
        System.out.println("parse(\"0\"): " + parse("0"));
        System.out.println("parse(\"forty\"): " + parse("forty"));
        System.out.println("a real zero and a failure look identical: "
                + (parse("0") == parse("forty")));
    }
}
