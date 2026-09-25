import java.util.ArrayList;
import java.util.List;

public class Sol1 {
    record Scores(String student, List<Integer> marks) {
        Scores {
            marks = List.copyOf(marks);
        }
    }

    public static void main(String[] args) {
        List<Integer> marks = new ArrayList<>(List.of(70, 80));
        Scores s = new Scores("Ada", marks);

        marks.set(0, 0);
        System.out.println("caller mutated = " + marks);
        System.out.println("defended       = " + s.marks());
        System.out.println("value kept     = " + (s.marks().get(0) == 70));
        System.out.println("equals works   = " + s.equals(new Scores("Ada", List.of(70, 80))));

        try {
            s.marks().set(0, 1);
        } catch (UnsupportedOperationException e) {
            System.out.println("immutable      = " + e.getClass().getSimpleName());
        }
    }
}
