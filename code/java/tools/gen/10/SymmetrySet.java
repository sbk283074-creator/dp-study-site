import java.util.HashSet;
import java.util.Set;

public class SymmetrySet {

    static class Parent {
        final String name;

        Parent(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Parent p && name.equals(p.name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static final class Child extends Parent {
        final int extra;

        Child(String name, int extra) {
            super(name);
            this.extra = extra;
        }

        @Override
        public boolean equals(Object other) {
            return other != null && other.getClass() == getClass()
                    && ((Child) other).extra == extra && name.equals(((Child) other).name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static Set<Parent> inOrder(Parent first, Parent second) {
        Set<Parent> seen = new HashSet<>();
        seen.add(first);
        seen.add(second);
        return seen;
    }

    public static void main(String[] args) {
        Parent p = new Parent("x");
        Child c = new Child("x", 1);

        System.out.println("parent.equals(child): " + p.equals(c));
        System.out.println("child.equals(parent): " + c.equals(p));

        Set<Parent> parentFirst = inOrder(p, c);
        Set<Parent> childFirst = inOrder(c, p);

        System.out.println("size after parent then child: " + parentFirst.size());
        System.out.println("size after child then parent: " + childFirst.size());
        System.out.println("the one-entry set reports contains(parent): " + childFirst.contains(p));
        System.out.println("the one-entry set reports contains(child): " + childFirst.contains(c));
    }
}
