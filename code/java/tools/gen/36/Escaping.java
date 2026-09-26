public final class Escaping {

    private Escaping() {
    }

    public static String html(String value) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            switch (value.charAt(i)) {
                case '&' -> out.append("&amp;");
                case '<' -> out.append("&lt;");
                case '>' -> out.append("&gt;");
                case '"' -> out.append("&quot;");
                case '\'' -> out.append("&#39;");
                default -> out.append(value.charAt(i));
            }
        }
        return out.toString();
    }
}
