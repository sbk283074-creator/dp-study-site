import java.util.List;

public class Scenario {

    static int process(String text) {
        try {
            return Integer.parseInt(text) * 2;
        } catch (Exception e) {
            return -1;
        }
    }

    public static void main(String[] args) {
        List<String> inputs = List.of("3", "4", "oops", "5");

        int total = 0;
        int failures = 0;
        for (String input : inputs) {
            int result = process(input);
            total += result;
            if (result == -1) {
                failures++;
            }
        }

        int truth = inputs.stream().filter(text -> text.matches("\\d+"))
                .mapToInt(Integer::parseInt).sum() * 2;

        System.out.println("rows: " + inputs.size());
        System.out.println("failures seen by the -1 sentinel: " + failures);
        System.out.println("reported total: " + total);
        System.out.println("true total of the valid rows: " + truth);
        System.out.println("the sentinel was added to the total: " + (total != truth));
        System.out.println("the error is exactly one sentinel: " + (truth - total));
    }
}
