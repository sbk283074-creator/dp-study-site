public class Sol4 {
    static final String HEADER = "# quill-2";

    static String upgrade(String text) {
        StringBuilder out = new StringBuilder(HEADER).append('\n');
        int id = 1;
        for (String line : text.split("\n", -1)) {
            if (line.isBlank() || line.startsWith("# ")) {
                continue;
            }
            String[] parts = line.split("\t", 3);
            if (parts.length != 3) {
                throw new IllegalArgumentException("cannot upgrade: " + line);
            }
            out.append(id++).append('\t')
                    .append(parts[1].replace("\\", "\\\\")).append('\t')
                    .append(parts[2].replace("\\", "\\\\")).append('\n');
        }
        return out.toString();
    }

    static String show(String s) {
        return "'" + s.replace("\n", "\\n").replace("\t", "\\t") + "'";
    }

    public static void main(String[] args) {
        String old = "1\tGroceries\tmilk and eggs\n2\tReading\tchapter 22\n";
        String upgraded = upgrade(old);

        System.out.println("before = " + show(old));
        System.out.println("after  = " + show(upgraded));
        System.out.println();
        System.out.println("the header was added and the ids were renumbered from 1");
    }
}
