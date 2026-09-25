public class NonSealed {
    sealed interface Node permits Leaf, Branch, Wildcard {}

    record Leaf(int value) implements Node {}
    record Branch(Node left, Node right) implements Node {}
    non-sealed interface Wildcard extends Node {}

    record Anything(String tag) implements Wildcard {}

    static String describe(Node n) {
        return switch (n) {
            case Leaf l -> "leaf " + l.value();
            case Branch b -> "branch of " + b.left() + " and " + b.right();
            case Wildcard w -> "wildcard " + w;
        };
    }

    public static void main(String[] args) {
        Node[] nodes = {
            new Leaf(1),
            new Branch(new Leaf(1), new Leaf(2)),
            new Anything("x"),
        };
        for (Node n : nodes) {
            System.out.println(describe(n));
        }
        System.out.println("permitted = " + java.util.Arrays.toString(
                java.util.Arrays.stream(Node.class.getPermittedSubclasses())
                      .map(Class::getSimpleName)
                      .toArray()));
    }
}
