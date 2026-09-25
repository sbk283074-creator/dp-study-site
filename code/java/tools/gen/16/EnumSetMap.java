import java.util.EnumMap;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class EnumSetMap {
    enum Day { MON, TUE, WED, THU, FRI, SAT, SUN }

    public static void main(String[] args) {
        Set<Day> weekend = EnumSet.of(Day.SUN, Day.SAT);
        System.out.println("EnumSet order  = " + weekend);

        EnumSet<Day> weekdays = EnumSet.complementOf(EnumSet.of(Day.SAT, Day.SUN));
        System.out.println("complement     = " + weekdays);

        Map<Day, Integer> counts = new EnumMap<>(Day.class);
        counts.put(Day.FRI, 3);
        counts.put(Day.MON, 1);
        counts.put(Day.WED, 2);
        System.out.println("EnumMap keys   = " + counts.keySet());
        System.out.println("EnumMap values = " + counts.values());

        Set<Day> hashSet = new HashSet<>(weekend);
        Map<Day, Integer> hashMap = new HashMap<>(counts);
        System.out.println("HashSet equal  = " + hashSet.equals(weekend));
        System.out.println("HashMap equal  = " + hashMap.equals(counts));
    }
}
