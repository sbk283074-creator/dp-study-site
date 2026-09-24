import java.util.Locale;

public class Sol3 {
    static final class Temperature {
        private final double celsius;

        private Temperature(double celsius) {
            this.celsius = celsius;
        }

        static Temperature celsius(double value) {
            return new Temperature(value);
        }

        static Temperature fahrenheit(double value) {
            return new Temperature((value - 32) * 5 / 9);
        }

        double celsius() {
            return celsius;
        }

        double fahrenheit() {
            return celsius * 9 / 5 + 32;
        }

        @Override
        public String toString() {
            return String.format(Locale.ROOT, "%.2f C / %.2f F", celsius, fahrenheit());
        }
    }

    public static void main(String[] args) {
        System.out.println("freezing = " + Temperature.celsius(0));
        System.out.println("boiling  = " + Temperature.celsius(100));
        System.out.println("body     = " + Temperature.fahrenheit(98.6));
        System.out.println("37 C in F = " + Temperature.celsius(37).fahrenheit());
        System.out.println("one stored representation, two factories and two accessors");
    }
}
