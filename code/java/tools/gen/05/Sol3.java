public class Sol3 {
    static String describe(Object value) {
        return switch (value) {
            case null -> "null";
            case Integer i when i < 0 -> "negative int";
            case Integer i -> "non-negative int";
            case String s when s.isEmpty() -> "empty string";
            case String s -> "string";
            case Boolean b -> "boolean";
            default -> "other";
        };
    }

    public static void main(String[] args) {
        Object[] samples = {null, -1, 0, "", "x", true, 1.5};

        int[] tally = new int[5];
        String[] labels = {"null", "negative int", "non-negative int", "empty string",
                "string"};
        for (Object sample : samples) {
            String arm = describe(sample);
            System.out.println(String.valueOf(sample) + " -> " + arm);
            for (int i = 0; i < labels.length; i++) {
                if (labels[i].equals(arm)) {
                    tally[i]++;
                }
            }
        }
        for (int i = 0; i < labels.length; i++) {
            System.out.println(labels[i] + " arm used " + tally[i] + " time(s)");
        }
    }
}
