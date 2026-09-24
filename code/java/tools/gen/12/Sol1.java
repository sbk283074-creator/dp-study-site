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
