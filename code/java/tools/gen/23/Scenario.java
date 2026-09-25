import java.util.ArrayList;
import java.util.List;

public class Scenario {
    static List<String> lines() {
        return new ArrayList<>(List.of(
                "# quill-2",
                "1\tGroceries\tmilk and eggs",
                "2\tReading\tchapter 23",
                "3\tDraft\tdelete me"));
    }

    static List<String> truncateAt(List<String> lines, int id) {
        for (int i = 0; i < lines.size(); i++) {
            if (lines.get(i).startsWith(id + "\t")) {
                return new ArrayList<>(lines.subList(0, i));
            }
        }
        return lines;
    }

    static List<String> filterOut(List<String> lines, int id) {
        List<String> kept = new ArrayList<>();
        for (String line : lines) {
            if (!line.startsWith(id + "\t")) {
                kept.add(line);
            }
        }
        return kept;
    }

    public static void main(String[] args) {
        System.out.println("before          = " + lines().size() + " line(s)");
        System.out.println("truncate at #1  = " + truncateAt(lines(), 1).size() + " line(s)");
        System.out.println("filter out #1   = " + filterOut(lines(), 1).size() + " line(s)");
        System.out.println();
        System.out.println("truncating keeps what came before the note and loses what came after");
    }
}
