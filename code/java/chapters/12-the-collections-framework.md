---
chapter: 12
part: 2
title: The Collections Framework
summary: Pick the right container for the question you are actually asking — and let the interface you choose say what you need.
minutes: 60
tags: [collections, List, Set, Map, TreeMap, Comparator, Comparable, iteration, immutability]
---

Chapter 10 was the contract objects must keep. This is the machinery that keeps it for you, and it is
the reason the contract mattered: `List`, `Set` and `Map` are three different *questions* about the
same data, and the collection you pick is a statement about which questions you will ask.

There are two skills here and they are separate. The first is choosing between the interfaces — a
`List` when order and duplicates matter, a `Set` when membership does, a `Map` when you are looking
things up by key. The second is choosing between the *implementations* of the one you picked, because
`HashSet`, `LinkedHashSet` and `TreeSet` all answer "is this in the set?" and differ entirely in what
they do with the order. Most collection bugs are a wrong choice in the second category: the code works,
the tests pass, and the output arrives in an order nobody chose.

## `List`: order, duplicates, and index

```java run
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

public class ListOps {

    public static void main(String[] args) {
        List<String> queue = new ArrayList<>(List.of("a", "b", "c"));

        System.out.println("start: " + queue);
        queue.add("d");
        System.out.println("add at the end: " + queue);
        queue.add(0, "z");
        System.out.println("add at index 0: " + queue);
        System.out.println("get(1): " + queue.get(1));
        System.out.println("indexOf(\"c\"): " + queue.indexOf("c"));
        System.out.println("remove(\"z\") returned: " + queue.remove("z"));
        System.out.println("remove(0) returned: " + queue.remove(0));
        System.out.println("after removals: " + queue);
        System.out.println("subList(1, 3): " + queue.subList(1, 3));
        System.out.println("size: " + queue.size());

        List<String> linked = new LinkedList<>(queue);
        System.out.println("a LinkedList holds the same: " + linked.equals(queue));
        System.out.println("both implement List: " + (queue instanceof List && linked instanceof List));
        System.out.println("but only one is RandomAccess: "
                + (queue instanceof java.util.RandomAccess) + " and "
                + (linked instanceof java.util.RandomAccess));
    }
}
```

```text
start: [a, b, c]
add at the end: [a, b, c, d]
add at index 0: [z, a, b, c, d]
get(1): a
indexOf("c"): 3
remove("z") returned: true
remove(0) returned: a
after removals: [b, c, d]
subList(1, 3): [c, d]
size: 3
a LinkedList holds the same: true
both implement List: true
but only one is RandomAccess: true and false
```

Every method here is the obvious one, and the reason to look at the list as a whole is the last three
lines. A `LinkedList` and an `ArrayList` both implement `List`, so both accept every method in the
table, and `linked.equals(queue)` is `true` — the *contract* is identical.

The difference is hidden behind a marker interface. `ArrayList` implements `RandomAccess` and
`LinkedList` does not, which is a promise about `get(i)`: constant time for one, linear for the other.
Nothing enforces it at the type level; it is a flag that algorithms like `Collections.binarySearch`
read to decide whether to use an index or an iterator.

:::note
Reach for `ArrayList` unless you have measured otherwise. `LinkedList` wins only when you are inserting
and removing at the ends of a very long list, and `ArrayDeque` beats it at that. In practice a
`LinkedList` in application code is almost always a default rather than a decision.
:::

## `Set`: the order question

A `Set` answers "have I seen this?" and the three implementations differ in the order they hand things
back.

```java run
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

public class SetOrders {

    public static void main(String[] args) {
        List<String> input = List.of("pear", "apple", "plum", "apple");

        Set<String> hash = new HashSet<>(input);
        Set<String> linked = new LinkedHashSet<>(input);
        Set<String> tree = new TreeSet<>(input);

        System.out.println("input: " + input);
        System.out.println("LinkedHashSet keeps arrival order: " + linked);
        System.out.println("TreeSet sorts: " + tree);
        System.out.println("all three hold the same elements: "
                + (hash.equals(linked) && linked.equals(tree)));
        System.out.println("the duplicates are gone: " + hash.size() + " of " + input.size());
        System.out.println("HashSet membership, not order: " + hash.contains("apple"));
    }
}
```

```text
input: [pear, apple, plum, apple]
LinkedHashSet keeps arrival order: [pear, apple, plum]
TreeSet sorts: [apple, pear, plum]
all three hold the same elements: true
the duplicates are gone: 3 of 4
HashSet membership, not order: true
```

The input has four elements and three survive, because `apple` arrived twice and a set does not hold
duplicates. That part is the same in all three.

The order is not. `LinkedHashSet` keeps arrival order, `TreeSet` sorts, and `HashSet` — the default,
and the one people reach for without thinking — gives an order derived from `hashCode` and meaningful
to nobody. It is *stable* for a given set of keys, which is what makes the bug so durable: it looks
like a deliberate order because it does not change between runs.

:::pitfall
**A `HashSet` is not "an unordered list" — it is a set with an order you did not choose and cannot
predict from the code.** The moment that order reaches a report, a file or a user, you have a defect
that will survive every test that compares sets rather than sequences. If order matters, say so in the
type: `LinkedHashSet` for arrival, `TreeSet` for sorted.
:::

## `Map`: the methods that remove the boilerplate

A `Map` is a lookup, and the modern API has collapsed the five-line patterns into one call each.

```java run
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class MapOps {

    public static void main(String[] args) {
        Map<String, Integer> counts = new HashMap<>();
        for (String word : List.of("a", "b", "a", "c", "a")) {
            counts.merge(word, 1, Integer::sum);
        }
        System.out.println("merged: " + new TreeMap<>(counts));

        Map<String, List<String>> grouped = new HashMap<>();
        for (String word : List.of("apple", "avocado", "banana")) {
            grouped.computeIfAbsent(word.substring(0, 1), key -> new ArrayList<>()).add(word);
        }
        System.out.println("grouped: " + new TreeMap<>(grouped));

        System.out.println("getOrDefault on a missing key: " + counts.getOrDefault("zzz", 0));
        System.out.println("putIfAbsent returns the value already there: "
                + counts.putIfAbsent("a", 99));
        System.out.println("so a is still: " + counts.get("a"));
        System.out.println("get on a missing key is: " + counts.get("zzz"));
        System.out.println("keys: " + new TreeMap<>(counts).keySet());
        System.out.println("values total: " + counts.values().stream().mapToInt(Integer::intValue).sum());
    }
}
```

```text
merged: {a=3, b=1, c=1}
grouped: {a=[apple, avocado], b=[banana]}
getOrDefault on a missing key: 0
putIfAbsent returns the value already there: 3
so a is still: 3
get on a missing key is: null
keys: [a, b, c]
values total: 5
```

`merge` is the counting idiom: `counts.merge(word, 1, Integer::sum)` means "if absent put 1, else
replace with the old value plus 1". `computeIfAbsent` is the grouping idiom, and note the shape — it
returns the value *that is now present*, so `.add(word)` attaches to the list you just created or the
one that was already there. Writing that by hand takes four lines and one of them is usually wrong.

The last four lines are the two ways a missing key behaves, and they are the opposite of each other.
`getOrDefault` gives you a value back; `get` gives you `null`, and `null` is not `0` — `counts.get("zzz")
+ 1` throws a `NullPointerException` while `counts.getOrDefault("zzz", 0) + 1` prints `1`. And
`putIfAbsent` returns the value that was *already there* (`3`), not the one you passed, which is how you
detect that you lost the race.

:::warning
A `Map` with a `null` value and a `Map` with no entry are different, and `get` cannot tell you which you
have. If `null` is a legal value in your map, use `containsKey` — or refuse to store `null` in the first
place, which is the cleaner rule and what `Map.of` enforces.
:::

## `NavigableMap`: the questions a sorted map can answer

`TreeMap` implements `NavigableMap`, and the extra methods are about *neighbours* rather than exact keys.

```java run
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
```

```text
all: {1=gold, 5=silver, 10=bronze}
floorEntry(4): 1=gold
ceilingEntry(4): 5=silver
floorEntry(5), an exact hit: 5=silver
ceilingEntry(11): null
headMap(5), exclusive: {1=gold}
tailMap(5), inclusive: {5=silver, 10=bronze}
descendingMap: {10=bronze, 5=silver, 1=gold}
firstKey / lastKey: 1 / 10
```

`floorEntry` gives the largest key that is not greater than the one you asked for; `ceilingEntry` gives
the smallest key that is not smaller. `floorEntry(4)` lands on `1=gold` and `ceilingEntry(4)` on
`5=silver`, and when there is nothing above, `ceilingEntry(11)` returns `null` rather than throwing.

This is the shape a tiered pricing table or a rate band wants: you store the *boundaries* and ask
"which band am I in" with one call, instead of looping over a list comparing ranges. `headMap` and
`tailMap` give you views — live views, so a change through either is visible in both.

## `Comparable` and `Comparator` are different jobs

`Comparable` is a property of a type: it says "objects of this class have a natural order". `Comparator`
is a standalone object that says "sort *these* by *this* rule". A class can have only one natural order
and any number of comparators.

```java run
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
```

```text
sorted as versions: [1.9, 1.10, 2.2, 2.10]
min: 1.9
max: 2.10
binarySearch finds 2.2 at index: 2
the same versions as text: [1.10, 1.9, 2.10, 2.2]
text order puts 2.10 before 2.2: true
```

`Version` implements `Comparable<Version>`, so `Collections.sort` works on it, and so do `min`, `max`
and `binarySearch` — all four are written against `Comparable` and get your ordering for free.

The last two lines are the reason the `compareTo` is written the long way. Sorting the same versions
*as text* gives `[1.10, 1.9, 2.10, 2.2]`, because `"1.10" < "1.9"` lexicographically. That is
numerically wrong, and it is exactly what you get if you store a version as a `String` and sort it —
a defect that appears only when a minor version reaches double digits.

When the order is not a property of the type — or when there are several plausible ones — use a
`Comparator`.

```java run
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

public class Comparators {

    record Person(String name, int age) {
    }

    static List<String> names(List<Person> people) {
        return people.stream().map(Person::name).toList();
    }

    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
            new Person("grace", 45), new Person("ada", 36),
            new Person("alan", 41), new Person("bob", 36)));

        people.sort(Comparator.comparing(Person::age));
        System.out.println("by age:                " + names(people));

        people.sort(Comparator.comparing(Person::age).thenComparing(Person::name));
        System.out.println("by age, then name:     " + names(people));

        people.sort(Comparator.comparing(Person::name).reversed());
        System.out.println("by name, reversed:     " + names(people));

        people.sort(Comparator.comparingInt(Person::age).reversed()
                .thenComparing(Person::name));
        System.out.println("oldest first, ties by name: " + names(people));

        List<String> words = new ArrayList<>(Arrays.asList("pear", null, "apple"));
        words.sort(Comparator.nullsLast(Comparator.naturalOrder()));
        System.out.println("nulls last:            " + words);

        Comparator<Person> byAge = Comparator.comparingInt(Person::age);
        System.out.println("reversing twice returns the original: "
                + (byAge.reversed().reversed().compare(people.get(0), people.get(1))
                   == byAge.compare(people.get(0), people.get(1))));
    }
}
```

```text
by age:                [ada, bob, alan, grace]
by age, then name:     [ada, bob, alan, grace]
by name, reversed:     [grace, bob, alan, ada]
oldest first, ties by name: [grace, alan, ada, bob]
nulls last:            [apple, pear, null]
reversing twice returns the original: true
```

`Comparator.comparing` builds one from a key extractor; `thenComparing` chains a tie-break; `reversed`
flips it. Read the first two lines together: sorting by age alone and sorting by age *then name* give
the same answer here, because `ada` and `bob` are both 36 and already in that order. The tie-break only
shows itself when the input order disagrees with it, which is why a comparator without a tie-break is a
latent bug rather than a visible one.

`nullsLast` is the piece people miss. A comparator that calls `compareTo` on a `null` key throws, and
the fix is to wrap it: `Comparator.nullsLast(Comparator.naturalOrder())` puts `null` at the end and
never asks it to compare itself.

:::tip
**Always give a sort a total order.** If two elements can compare equal, the sort is free to leave them
in any relative order — and `List.sort` is stable, so it will leave them in the *input* order, which
means your report's layout depends on how the data happened to arrive. Add a tie-break on a unique
field and the output stops being an accident.
:::

## Immutable collections, and the two failures they prevent

`List.of`, `Set.of` and `Map.of` build collections that cannot change.

```java run
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

public class Immutable {

    public static void main(String[] args) {
        List<String> fixed = List.of("a", "b");
        Set<String> unique = Set.of("a", "b");
        Map<String, Integer> counts = Map.of("a", 1, "b", 2);

        System.out.println("List.of: " + fixed);
        System.out.println("Set.of, printed in sorted order: " + new TreeSet<>(unique));
        System.out.println("Map.of: " + new TreeMap<>(counts));

        List<String> copy = new ArrayList<>(fixed);
        copy.add("c");
        System.out.println("a defensive copy can grow: " + copy);
        System.out.println("the original is untouched: " + fixed);

        List<String> alsoCopy = List.copyOf(fixed);
        System.out.println("List.copyOf is also immutable: " + alsoCopy);
        System.out.println("it is a different object from the source: " + (alsoCopy != fixed));
        System.out.println("but equal to it: " + alsoCopy.equals(fixed));
    }
}
```

```text
List.of: [a, b]
Set.of, printed in sorted order: [a, b]
Map.of: {a=1, b=2}
a defensive copy can grow: [a, b, c]
the original is untouched: [a, b]
List.copyOf is also immutable: [a, b]
it is a different object from the source: false
but equal to it: true
```

`List.of` and friends are the right default for a value that is handed around: nothing downstream can
add to it, clear it, or sort it in place. They reject `null` outright, which is why `List.of(a, b)` is
a stronger promise than `Arrays.asList(a, b)`.

The last three lines contain a surprise worth knowing. `List.copyOf` returns an *immutable* list, and
if the argument is already one it may return **the same object** — so `alsoCopy != fixed` is `false`.
That is legal because the two are indistinguishable: an immutable object has no identity-dependent
behaviour, so sharing one is safe. Do not write code that depends on `copyOf` returning a fresh
instance.

What happens when you forget they are immutable is worth seeing once.

```java throw
import java.util.List;

public class ImmutableAdd {

    public static void main(String[] args) {
        List<String> fixed = List.of("a", "b");
        fixed.add("c");
        System.out.println("never reached: " + fixed);
    }
}
```

```text
Exception in thread "main" java.lang.UnsupportedOperationException
```

`UnsupportedOperationException` from `ImmutableCollections.add`. Note the stack trace: the exception is
thrown inside `add`, at the call site, and it names the line that did it — which is the whole reason an
immutable collection is a *better* failure than a mutable one that quietly changes underneath a caller.

## Iterating and modifying at the same time

This is the collection bug that bites hardest, and it has two faces.

```java run
import java.util.ArrayList;
import java.util.List;

public class CmeSilent {

    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("ada", "bob", "cal"));

        int examined = 0;
        for (String name : names) {
            examined++;
            if (name.startsWith("b")) {
                names.remove(name);
            }
        }

        System.out.println("no exception was thrown: " + names);
        System.out.println("elements examined: " + examined + " of 3");
        System.out.println("the last one was never looked at: " + (examined < 3));
    }
}
```

```text
no exception was thrown: [ada, cal]
elements examined: 2 of 3
the last one was never looked at: true
```

No exception. The list came out correct. And the loop **examined two of the three elements** — `cal` was
never looked at, because removing `bob` shrank the list while the iterator was still counting, and
`hasNext()` compared a cursor against a size that had just changed.

The output is right by luck. Change one character and it is not.

```java throw
import java.util.ArrayList;
import java.util.List;

public class CmeRemove {

    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("ada", "bob", "cal", "ben"));

        for (String name : names) {
            if (name.startsWith("b")) {
                names.remove(name);
            }
        }

        System.out.println("never reached: " + names);
    }
}
```

```text
Exception in thread "main" java.util.ConcurrentModificationException
```

Four elements, and now the iterator catches it: `ConcurrentModificationException`. The difference is
that after removing `bob` there is still an element to visit, so `next()` runs its modification check
and fails. **The same bug is silent or fatal depending only on the length of the input**, which is why
this defect ships: it is tested with three items and fails in production with four.

:::danger
**Never modify a collection inside a for-each loop over it.** Use `iterator.remove()`, which is the one
removal the iterator knows about, or `Collection.removeIf`, or build a new collection with a stream
filter. The for-each loop is implemented on an iterator you cannot see, so you cannot tell it what you
did.
:::

## Equality is what makes a set a set

Chapter 10 said collections depend on the `equals`/`hashCode` contract. Here is what it looks like when
the contract is missing.

```java run
import java.util.HashSet;
import java.util.Set;

public class EqualityInSets {

    static final class WithoutEquals {
        final String id;

        WithoutEquals(String id) {
            this.id = id;
        }
    }

    record WithEquals(String id) {
    }

    public static void main(String[] args) {
        Set<WithoutEquals> identity = new HashSet<>();
        identity.add(new WithoutEquals("A"));
        identity.add(new WithoutEquals("A"));

        Set<WithEquals> value = new HashSet<>();
        value.add(new WithEquals("A"));
        value.add(new WithEquals("A"));

        System.out.println("identity keys give: " + identity.size() + " entries");
        System.out.println("value keys give: " + value.size() + " entry");
        System.out.println("contains on the identity set: "
                + identity.contains(new WithoutEquals("A")));
        System.out.println("contains on the value set: "
                + value.contains(new WithEquals("A")));
    }
}
```

```text
identity keys give: 2 entries
value keys give: 1 entry
contains on the identity set: false
contains on the value set: true
```

`WithoutEquals` inherits identity from `Object`, so two badges with the same `id` are two different
values as far as the set is concerned: `2 entries`, and `contains` answers `false` for an object that
is plainly in there. `WithEquals` is a `record`, so the compiler wrote the pair, and it behaves: `1
entry`, `contains` returns `true`.

Nothing in this chapter works properly without that contract, and nothing warns you when it is absent.
The type system will happily let you put a key into a `HashMap` that can never be found again.

:::scenario The report whose row order nobody chose

A nightly job groups sales by region and prints a summary. The numbers are right. The order is not.

:::solution
The rows come out of a `HashMap`, so their order is derived from `hashCode` and has nothing to do with
the data. It is stable for a given set of keys, which is what makes it look intentional — until a new
region is added and the whole report reshuffles.

```java run
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Scenario {

    public static void main(String[] args) {
        List<String> regions = List.of("west", "east", "north", "south", "east", "west", "west");

        Map<String, Integer> hash = new HashMap<>();
        Map<String, Integer> linked = new LinkedHashMap<>();
        Map<String, Integer> tree = new TreeMap<>();
        for (String region : regions) {
            for (Map<String, Integer> target : List.of(hash, linked, tree)) {
                target.merge(region, 1, Integer::sum);
            }
        }

        List<String> hashOrder = new ArrayList<>(hash.keySet());
        List<String> linkedOrder = new ArrayList<>(linked.keySet());
        List<String> treeOrder = new ArrayList<>(tree.keySet());
        List<String> sortedOrder = new ArrayList<>(linkedOrder);
        Collections.sort(sortedOrder);

        System.out.println("rows: " + regions.size() + ", distinct regions: " + hash.size());
        System.out.println("HashMap order:       " + hashOrder);
        System.out.println("LinkedHashMap order: " + linkedOrder);
        System.out.println("TreeMap order:       " + treeOrder);
        System.out.println("LinkedHashMap is the arrival order: "
                + linkedOrder.equals(List.of("west", "east", "north", "south")));
        System.out.println("TreeMap is sorted: " + treeOrder.equals(sortedOrder));
        System.out.println("HashMap is sorted: " + hashOrder.equals(sortedOrder));
        System.out.println("all three agree on the counts: "
                + (hash.equals(tree) && tree.equals(linked)));
    }
}
```

```text
rows: 7, distinct regions: 4
HashMap order:       [east, south, north, west]
LinkedHashMap order: [west, east, north, south]
TreeMap order:       [east, north, south, west]
LinkedHashMap is the arrival order: true
TreeMap is sorted: true
HashMap is sorted: false
all three agree on the counts: true
```

The three maps hold **identical counts** — the last line confirms it — and they print in three
different orders. `LinkedHashMap` gives `[west, east, north, south]`, which is the order the rows
arrived. `TreeMap` gives `[east, north, south, west]`, which is sorted. `HashMap` gives
`[east, south, north, west]`, which is neither.

Notice what is *not* wrong here. The counts are correct, the code is idiomatic, and no test that
compares maps rather than sequences will ever catch it. The defect is entirely in a choice that was
never made deliberately — `new HashMap<>()` was typed out of habit, and the report inherited an order
from a hash function.

The fix is to decide, and to put the decision in the type: `LinkedHashMap` if the report should read in
arrival order, `TreeMap` if it should be sorted. Either is defensible. `HashMap` is not, because it is
not an answer to the question the report is asking.
:::

## Solutions

### 1. Let the container do the work

```java run
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public class Sol1 {

    static final class Word {
        static int comparisons = 0;

        final String text;

        Word(String text) {
            this.text = text;
        }

        @Override
        public boolean equals(Object other) {
            comparisons++;
            return other instanceof Word word && word.text.equals(text);
        }

        @Override
        public int hashCode() {
            return text.hashCode();
        }

        @Override
        public String toString() {
            return text;
        }
    }

    static List<Word> dedupeByList(List<Word> words) {
        List<Word> seen = new ArrayList<>();
        for (Word word : words) {
            if (!seen.contains(word)) {
                seen.add(word);
            }
        }
        return seen;
    }

    static Set<Word> dedupeBySet(List<Word> words) {
        return new LinkedHashSet<>(words);
    }

    public static void main(String[] args) {
        List<Word> words = new ArrayList<>();
        for (int i = 0; i < 200; i++) {
            words.add(new Word("w" + (i % 20)));
        }

        Word.comparisons = 0;
        List<Word> byList = dedupeByList(words);
        int listComparisons = Word.comparisons;

        Word.comparisons = 0;
        Set<Word> bySet = dedupeBySet(words);
        int setComparisons = Word.comparisons;

        System.out.println("words in: " + words.size());
        System.out.println("distinct words: " + byList.size());
        System.out.println("List.contains needed " + listComparisons + " equals calls");
        System.out.println("LinkedHashSet needed " + setComparisons + " equals calls");
        System.out.println("the set did less work: " + (setComparisons < listComparisons));
        System.out.println("and both kept arrival order: "
                + byList.toString().equals(bySet.toString()));
    }
}
```

```text
words in: 200
distinct words: 20
List.contains needed 2080 equals calls
LinkedHashSet needed 180 equals calls
the set did less work: true
and both kept arrival order: true
```

Two hundred words, twenty distinct. `List.contains` inside a loop asks the question by scanning, so it
cost **2,080** `equals` calls; a `LinkedHashSet` hashes once per word and needs **180**. The ratio grows
with the square of the input, which is the difference between a helper that is fine in a test and one
that is not fine in a job.

Both answers are identical — `and both kept arrival order: true` — so this is a pure cost change with no
behavioural risk. That is the easiest kind of improvement to make and the easiest to skip, because
nothing is visibly broken.

The counting is done by a static counter inside `Word.equals`, which is worth noticing as a technique:
to find out how many comparisons an algorithm makes, put the counter in the object being compared, not
in the algorithm.

### 2. Make the sort a total order

```java run
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;

public class Sol2 {

    record Entry(String name, int score) {
    }

    static List<String> names(List<Entry> entries) {
        return entries.stream().map(Entry::name).toList();
    }

    public static void main(String[] args) {
        List<Entry> entries = new ArrayList<>(List.of(
            new Entry("eve", 90), new Entry("bob", 75), new Entry("ada", 90),
            new Entry("dee", 75), new Entry("cal", 90)));

        List<Entry> stable = new ArrayList<>(entries);
        stable.sort(Comparator.comparingInt(Entry::score).reversed());
        System.out.println("by score alone, ties keep arrival order: " + names(stable));

        List<Entry> byName = new ArrayList<>(entries);
        byName.sort(Comparator.comparingInt(Entry::score).reversed()
                .thenComparing(Entry::name));
        System.out.println("by score, then name: " + names(byName));

        System.out.println("the tied group is the same three people: "
                + (new HashSet<>(names(stable).subList(0, 3))
                        .equals(new HashSet<>(names(byName).subList(0, 3)))));
        System.out.println("but the order inside it differs: "
                + !names(stable).equals(names(byName)));
    }
}
```

```text
by score alone, ties keep arrival order: [eve, ada, cal, bob, dee]
by score, then name: [ada, cal, eve, bob, dee]
the tied group is the same three people: true
but the order inside it differs: true
```

Sorting by score alone puts the three 90s in `[eve, ada, cal]` — the order they arrived, because
`List.sort` is stable. Adding `thenComparing(Entry::name)` gives `[ada, cal, eve]`. The tied group is
the same three people either way, and the order inside it is the difference between a report that is
reproducible and one that depends on the input order.

The tie-break costs one line and removes an entire class of "it looked different yesterday" bug.

### 3. Build the report you actually want to read

```java run
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Sol3 {

    record Sale(String region, String product, int units) {
    }

    public static void main(String[] args) {
        List<Sale> sales = List.of(
            new Sale("north", "pen", 3), new Sale("south", "pen", 5),
            new Sale("north", "ink", 2), new Sale("south", "ink", 1),
            new Sale("north", "pen", 4));

        Map<String, Integer> byRegion = new TreeMap<>();
        for (Sale sale : sales) {
            byRegion.merge(sale.region(), sale.units(), Integer::sum);
        }
        System.out.println("units by region: " + byRegion);

        Map<String, Map<String, Integer>> nested = new TreeMap<>();
        for (Sale sale : sales) {
            nested.computeIfAbsent(sale.region(), key -> new TreeMap<>())
                  .merge(sale.product(), sale.units(), Integer::sum);
        }
        nested.forEach((region, products) ->
                System.out.println("  " + region + " -> " + products));

        int total = sales.stream().mapToInt(Sale::units).sum();
        System.out.println("total units: " + total);
        System.out.println("the regions sum to the total: "
                + (byRegion.values().stream().mapToInt(Integer::intValue).sum() == total));
    }
}
```

```text
units by region: {north=9, south=6}
  north -> {ink=2, pen=7}
  south -> {ink=1, pen=5}
total units: 15
the regions sum to the total: true
```

`TreeMap` for the outer map makes the regions sorted; a second `TreeMap` inside makes the products
sorted within each region; `merge` accumulates and `computeIfAbsent` groups. The result prints in an
order that a reader can predict, and the last line is the check that matters — the parts sum to the
whole, so the grouping has not lost anything.

That check is worth writing even in throwaway code. Grouping bugs are silent: a `merge` with the wrong
key, or a `computeIfAbsent` whose function returns a shared list, produces a report that looks plausible
and totals wrong.

### 4. Remove without breaking the loop

```java run
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class Sol4 {

    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("ada", "bob", "cal", "ben"));

        List<String> byRemoveIf = new ArrayList<>(names);
        byRemoveIf.removeIf(name -> name.startsWith("b"));
        System.out.println("removeIf: " + byRemoveIf);

        List<String> byIterator = new ArrayList<>(names);
        Iterator<String> iterator = byIterator.iterator();
        while (iterator.hasNext()) {
            if (iterator.next().startsWith("b")) {
                iterator.remove();
            }
        }
        System.out.println("iterator.remove: " + byIterator);

        System.out.println("the two agree: " + byRemoveIf.equals(byIterator));

        List<String> byFilter = names.stream().filter(name -> !name.startsWith("b")).toList();
        System.out.println("filter into a new list: " + byFilter);
        System.out.println("the original is untouched: " + names);
    }
}
```

```text
removeIf: [ada, cal]
iterator.remove: [ada, cal]
the two agree: true
filter into a new list: [ada, cal]
the original is untouched: [ada, bob, cal, ben]
```

`removeIf` is the one-liner, and `iterator.remove()` is what it does underneath — that is why both give
`[ada, cal]`. The iterator's `remove` is the only modification the iteration machinery knows to expect,
which is exactly what the for-each loop cannot give you.

The stream version is a third option and it is the safest of the three: `filter` builds a *new* list and
leaves the original untouched (`[ada, bob, cal, ben]`). When you are unsure whether something else holds
a reference to the collection, prefer producing a new one over mutating the old one — the class of bug
in the previous section cannot happen if nothing is being modified.

:::tip
Choose by what the caller expects. `removeIf` when the collection is yours and the mutation is the
point; a `filter` into a new list when the value might be shared. `iterator.remove()` when you need to
do something more complex per element than a predicate can express.
:::

## Key takeaways

- `List`, `Set` and `Map` are three questions about the same data. Pick the interface by the question,
  then the implementation by the order you need.
- `ArrayList` and `LinkedList` satisfy the same `List` contract and differ in `get(i)` cost;
  `RandomAccess` is the marker interface that tells an algorithm which it has.
- `HashSet` has an order derived from `hashCode` and meaningless to a reader. It is stable for a given
  set of keys, which is why the bug survives testing. Use `LinkedHashSet` or `TreeSet` when order
  matters.
- `merge`, `computeIfAbsent`, `getOrDefault` and `putIfAbsent` replace the boilerplate patterns, and
  `putIfAbsent` returns the value that was *already there*.
- `NavigableMap` answers neighbour questions — `floorEntry`, `ceilingEntry`, `headMap`, `tailMap` — and
  is the right shape for bands and tiers.
- `Comparable` is a property of the type; `Comparator` is a separate object. Give every sort a total
  order with a tie-break on a unique field, or its output depends on the input order.
- `List.of`, `Set.of` and `Map.of` are immutable and reject `null`. `List.copyOf` may return the same
  instance you passed in, so do not depend on it copying.
- Modifying a collection inside a for-each loop is silent with three elements and fatal with four. Use
  `removeIf`, `iterator.remove()`, or a stream that builds a new collection.
- A `HashSet` of objects without `equals` holds every one of them. The contract from Chapter 10 is what
  makes every collection in this chapter work.

## Practice

- [ ] Build a word-frequency report from a paragraph twice: once with `HashMap`, once with `TreeMap`.
      Write down which one you would ship and why.
- [ ] Store a version as a `String` and sort it. Find the smallest input that comes out wrong, then fix
      it with a `Comparable` type.
- [ ] Write a `Comparator<Person>` that sorts by last name, then first name, then date of birth. Say
      which of the three is the tie-break and which are the keys.
- [ ] Implement a rate band with a `NavigableMap<Integer, Double>` keyed by threshold, and find the band
      for a value with one call. Then do it with a `List` and a loop, and count the comparisons.
- [ ] Take the `CmeSilent` program and add a fourth name. Explain the two different outcomes from the
      length of the list alone.
- [ ] Write a method that returns `List.copyOf(input)`, then prove by reflection or identity that it
      sometimes returns its argument.

## Solutions to the practice problems

The practice problems are open-ended by design. Sketch answers, in order:

1. `TreeMap` for anything a human reads, because sorted output is reproducible and diffable. `HashMap`
   only when the map is never iterated — a pure lookup table.
2. Two versions where the text order differs from the numeric order, for example `1.9` and `1.10`.
   Sorting as text gives `1.10` first, which is numerically wrong.
3. Keys: last name, then first name. Tie-break: date of birth, which is unique in practice. A tie-break
   that is not unique leaves the order to the input.
4. `bands.floorEntry(value)` returns the whole band in one lookup. The `List` version scans every
   threshold, which is O(n) per lookup and O(n·m) for m lookups.
5. With three names the loop silently ends early after the removal; with four, `next()` runs its
   modification check and throws `ConcurrentModificationException`. Same bug, different input length.
6. `List.copyOf(listOfAB) == listOfAB` is `true`, because an immutable list has no identity-dependent
   behaviour and can safely be shared.
