import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Sol4 {
    static final class Version implements Comparable<Version> {
        private final int major;
        private final int minor;

        Version(int major, int minor) {
            this.major = major;
            this.minor = minor;
        }

        @Override
        public int compareTo(Version other) {
            if (major != other.major) {
                return Integer.compare(major, other.major);
            }
            return Integer.compare(minor, other.minor);
        }

        @Override
        public String toString() {
            return major + "." + minor;
        }
    }

    public static void main(String[] args) {
        List<Version> versions = new ArrayList<>(List.of(
                new Version(2, 10), new Version(1, 9), new Version(2, 2), new Version(1, 10)));

        System.out.println("before sort: " + versions);
        Collections.sort(versions);
        System.out.println("after sort : " + versions);
        System.out.println("max is " + Collections.max(versions));

        System.out.println("1.9 sorts before 1.10, which sorting the text would get wrong: "
                + (versions.get(0).compareTo(versions.get(1)) < 0));
    }
}
