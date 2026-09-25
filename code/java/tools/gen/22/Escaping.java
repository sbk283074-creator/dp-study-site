public class Escaping {
    static String wrongOrder(String field) {
        return field.replace("\n", "\\n").replace("\\", "\\\\");
    }

    static String rightOrder(String field) {
        return field.replace("\\", "\\\\").replace("\n", "\\n");
    }

    static String unescape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            char c = field.charAt(i);
            if (c != '\\') {
                out.append(c);
                continue;
            }
            i++;
            switch (field.charAt(i)) {
                case '\\' -> out.append('\\');
                case 'n' -> out.append('\n');
                case 't' -> out.append('\t');
                default -> throw new IllegalArgumentException("unknown escape");
            }
        }
        return out.toString();
    }

    static String show(String s) {
        return "'" + s.replace("\\", "\\\\").replace("\n", "\\n")
                .replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String[] fields = {"two\nlines", "back\\slash"};

        for (String field : fields) {
            System.out.println("field   = " + show(field));
            for (String name : new String[] {"wrongOrder", "rightOrder"}) {
                String stored = name.equals("wrongOrder")
                        ? wrongOrder(field)
                        : rightOrder(field);
                String back = unescape(stored);
                System.out.printf("  %-10s stored %-20s back %-20s same=%b%n",
                        name, stored, show(back), back.equals(field));
            }
        }
    }
}
