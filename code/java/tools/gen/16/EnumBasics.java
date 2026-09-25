public class EnumBasics {
    enum Planet {
        MERCURY(3.303e+23, 2.4397e6),
        EARTH(5.976e+24, 6.37814e6),
        MARS(6.421e+23, 3.3972e6);

        private final double mass;    // kilograms
        private final double radius;  // metres

        Planet(double mass, double radius) {
            this.mass = mass;
            this.radius = radius;
        }

        double surfaceGravity() {
            return 6.67300E-11 * mass / (radius * radius);
        }

        double surfaceWeight(double otherMass) {
            return otherMass * surfaceGravity();
        }
    }

    public static void main(String[] args) {
        System.out.printf("count   = %d%n", Planet.values().length);
        for (Planet p : Planet.values()) {
            System.out.printf("%-8s ordinal=%d gravity=%.2f%n", p, p.ordinal(), p.surfaceGravity());
        }
        System.out.println("valueOf = " + Planet.valueOf("MARS"));
        System.out.println("name    = " + Planet.EARTH.name());
        System.out.printf("75kg on MARS = %.2f%n", Planet.MARS.surfaceWeight(75));
    }
}
