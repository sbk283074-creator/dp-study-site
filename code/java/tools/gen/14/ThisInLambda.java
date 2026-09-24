public class ThisInLambda {

    String label = "outer field";

    Runnable viaLambda() {
        return () -> System.out.println("lambda sees this.label = " + this.label);
    }

    Runnable viaAnonymous() {
        return new Runnable() {
            String label = "anonymous field";

            @Override
            public void run() {
                System.out.println("anonymous sees this.label = " + this.label);
            }
        };
    }

    public static void main(String[] args) {
        ThisInLambda outer = new ThisInLambda();
        outer.viaLambda().run();
        outer.viaAnonymous().run();
        System.out.println("a lambda does not introduce a new this");
    }
}
