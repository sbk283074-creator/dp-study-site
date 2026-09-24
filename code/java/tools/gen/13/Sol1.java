import java.util.ArrayList;
import java.util.List;

public class Sol1 {

    record Result(int value, String error) {
        static Result ok(int value) {
            return new Result(value, null);
        }

        static Result failed(String error) {
            return new Result(0, error);
        }

        boolean isOk() {
            return error == null;
        }
    }

    static Result process(String text) {
        try {
            return Result.ok(Integer.parseInt(text) * 2);
        } catch (NumberFormatException e) {
            return Result.failed(text + " is not a number");
        }
    }

    public static void main(String[] args) {
        List<String> inputs = List.of("3", "4", "oops", "5");

        List<Result> results = new ArrayList<>();
        for (String input : inputs) {
            results.add(process(input));
        }

        int total = results.stream().filter(Result::isOk).mapToInt(Result::value).sum();
        List<String> errors = results.stream().filter(r -> !r.isOk()).map(Result::error).toList();

        System.out.println("rows: " + inputs.size());
        System.out.println("ok: " + results.stream().filter(Result::isOk).count());
        System.out.println("failed: " + errors.size() + " -> " + errors);
        System.out.println("total of the valid rows: " + total);
    }
}
