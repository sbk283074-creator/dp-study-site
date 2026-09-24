import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class NaturalOrder {

    record Version(int major, int minor) implements Comparable<Version> {
        @Override
        public int compareTo(Version other) {
            int byMajor = Integer.compare(major, other.major);
            return byMajor != 0 ? byMajor : Integer.compare(minor, other.minor);
        }

        @Override
        public String toString() {
            return major + "." + minor;
        }
    }

    public static void main(String[] args) {
        List<Version> versions = new ArrayList<>(List.of(
            new Version(1, 10), new Version(2, 2), new Version(1, 9), new Version(2, 10)));

        Collections.sort(versions);
        System.out.println("sorted as versions: " + versions);
        System.out.println("min: " + Collections.min(versions));
        System.out.println("max: " + Collections.max(versions));
        System.out.println("binarySearch finds 2.2 at index: "
                + Collections.binarySearch(versions, new Version(2, 2)));

        List<String> asText = new ArrayList<>(List.of("1.10", "2.2", "1.9", "2.10"));
        Collections.sort(asText);
        System.out.println("the same versions as text: " + asText);
        System.out.println("text order puts 2.10 before 2.2: "
                + (asText.indexOf("2.10") < asText.indexOf("2.2")));
    }
}
