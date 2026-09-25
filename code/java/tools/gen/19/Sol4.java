public class Sol4 {
    static int lastIndex(String haystack, String needle) {
        return haystack.lastIndexOf(needle);
    }

    static boolean has(String haystack, String needle) {
        return lastIndex(haystack, needle) >= 0;
    }

    public static void main(String[] args) {
        System.out.println("found     = " + lastIndex("banana", "an"));
        System.out.println("missing   = " + lastIndex("banana", "zz"));
        System.out.println("empty     = " + lastIndex("banana", ""));
        System.out.println("whole     = " + lastIndex("banana", "banana"));
        System.out.println("has an    = " + has("banana", "an"));
        System.out.println("has zz    = " + has("banana", "zz"));
    }
}
