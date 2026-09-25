public record Note(int id, String title, String body) {
    static final String SEP = "\t";

    String render() {
        return id + SEP + title + SEP + body;
    }

    static Note parse(String line) {
        String[] parts = line.split(SEP, 3);
        if (parts.length != 3) {
            throw new IllegalArgumentException("not a note line: " + line);
        }
        return new Note(Integer.parseInt(parts[0]), parts[1], parts[2]);
    }
}
