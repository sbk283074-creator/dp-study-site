public class RecordPattern {
    sealed interface Expr permits Num, Add, Mul {}

    record Num(double value) implements Expr {}
    record Add(Expr left, Expr right) implements Expr {}
    record Mul(Expr left, Expr right) implements Expr {}

    static double eval(Expr e) {
        return switch (e) {
            case Num(double v) -> v;
            case Add(var l, var r) -> eval(l) + eval(r);
            case Mul(var l, var r) -> eval(l) * eval(r);
        };
    }

    public static void main(String[] args) {
        Expr e = new Add(new Num(2), new Mul(new Num(3), new Num(4)));
        System.out.println("expr = " + e);
        System.out.printf("eval = %.1f%n", eval(e));
    }
}
