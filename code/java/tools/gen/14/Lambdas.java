public class Lambdas {

    interface Transform {
        String apply(String text);
    }

    public static void main(String[] args) {
        Transform upper = text -> text.toUpperCase();
        Transform exclaim = text -> text + "!";
        Transform anonymous = new Transform() {
            @Override
            public String apply(String text) {
                return text.toUpperCase();
            }
        };

        System.out.println("lambda: " + upper.apply("ada"));
        System.out.println("chained: " + exclaim.apply(upper.apply("ada")));
        System.out.println("anonymous class: " + anonymous.apply("ada"));
        System.out.println("both are Transform instances: "
                + (upper instanceof Transform) + " and " + (anonymous instanceof Transform));
        System.out.println("they are different classes: "
                + (upper.getClass() != anonymous.getClass()));
        System.out.println("the lambda body is the only thing you had to write");
    }
}
