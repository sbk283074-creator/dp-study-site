import java.util.NavigableMap;
import java.util.TreeMap;

public class Navigable {

    public static void main(String[] args) {
        NavigableMap<Integer, String> ranks = new TreeMap<>();
        ranks.put(1, "gold");
        ranks.put(5, "silver");
        ranks.put(10, "bronze");

        System.out.println("all: " + ranks);
        System.out.println("floorEntry(4): " + ranks.floorEntry(4));
        System.out.println("ceilingEntry(4): " + ranks.ceilingEntry(4));
        System.out.println("floorEntry(5), an exact hit: " + ranks.floorEntry(5));
        System.out.println("ceilingEntry(11): " + ranks.ceilingEntry(11));
        System.out.println("headMap(5), exclusive: " + ranks.headMap(5));
        System.out.println("tailMap(5), inclusive: " + ranks.tailMap(5));
        System.out.println("descendingMap: " + ranks.descendingMap());
        System.out.println("firstKey / lastKey: " + ranks.firstKey() + " / " + ranks.lastKey());
    }
}
