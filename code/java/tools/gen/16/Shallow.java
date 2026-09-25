import java.util.Arrays;

public class Shallow {
    record Scores(String student, int[] marks) {}

    public static void main(String[] args) {
        int[] marks = {70, 80};
        Scores s = new Scores("Ada", marks);
        System.out.println("stored          = " + Arrays.toString(s.marks()));

        marks[0] = 0;
        System.out.println("caller mutated  = " + Arrays.toString(s.marks()));

        s.marks()[1] = 0;
        System.out.println("accessor mutated= " + Arrays.toString(s.marks()));

        System.out.println("equals a copy   = " + s.equals(new Scores("Ada", new int[] {0, 0})));
        System.out.println("same contents   = " + Arrays.equals(s.marks(), new int[] {0, 0}));
    }
}
