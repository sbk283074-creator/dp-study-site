public record Note(int id, String title, String body) {
    static final String SEP = "\t";

    public Note {
        if (id <= 0) {
            throw new IllegalArgumentException("id must be positive: " + id);
        }
    }

    String render() {
        return id + SEP + escape(title) + SEP + escape(body);
    }

    static Note parse(String line) {
        String[] parts = line.split(SEP, 3);
        if (parts.length != 3) {
            throw new IllegalArgumentException("not a note line: " + line);
        }
        return new Note(Integer.parseInt(parts[0]), unescape(parts[1]), unescape(parts[2]));
    }

    static String escape(String field) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < field.length(); i++) {
            switch (field.charAt(i)) {
                case '\\' -> out.append("\\\\");
                case '\t' -> out.append("\\t");
                case '\n' -> out.append("\\n");
                case '\r' -> out.append("\\r");
                default -> out.append(field.charAt(i));
            }
        }
        return out.toString();
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
            if (i == field.length()) {
                throw new IllegalArgumentException("trailing backslash in field");
            }
            switch (field.charAt(i)) {
                case '\\' -> out.append('\\');
                case 't' -> out.append('\t');
                case 'n' -> out.append('\n');
                case 'r' -> out.append('\r');
                default -> throw new IllegalArgumentException(
                        "unknown escape: \\" + field.charAt(i));
            }
        }
        return out.toString();
    }
}
