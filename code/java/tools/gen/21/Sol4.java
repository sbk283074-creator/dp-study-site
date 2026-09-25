public class Sol4 {
    static String stripCarriageReturn(String line) {
        int end = line.length();
        while (end > 0 && line.charAt(end - 1) == '\r') {
            end--;
        }
        return line.substring(0, end);
    }

    public static void main(String[] args) {
        String[] lines = {
            "1\tGroceries\tmilk and eggs\r",
            "2\tReading\tchapter 21",
            "3\tOdd\ttwo\r\r",
        };

        for (String raw : lines) {
            String clean = stripCarriageReturn(raw);
            String body = clean.split("\t", 3)[2];
            System.out.printf("%-40s body='%s' length=%d%n",
                    "'" + raw.replace("\t", "\\t").replace("\r", "\\r") + "'",
                    body, body.length());
        }

        System.out.println();
        System.out.println("every body is now free of a carriage return");
    }
}
