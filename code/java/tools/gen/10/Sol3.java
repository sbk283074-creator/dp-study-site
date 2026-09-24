public class Sol3 {

    static class Colour {
        final String name;

        Colour(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Colour c && name.equals(c.name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static final class Rgb extends Colour {
        final int rgb;

        Rgb(String name, int rgb) {
            super(name);
            this.rgb = rgb;
        }

        @Override
        public boolean equals(Object other) {
            return other instanceof Rgb r && r.rgb == rgb && name.equals(r.name);
        }

        @Override
        public int hashCode() {
            return name.hashCode() * 31 + rgb;
        }
    }

    static class StrictColour {
        final String name;

        StrictColour(String name) {
            this.name = name;
        }

        @Override
        public boolean equals(Object other) {
            return other != null && other.getClass() == getClass()
                    && name.equals(((StrictColour) other).name);
        }

        @Override
        public int hashCode() {
            return name.hashCode();
        }
    }

    static final class StrictRgb extends StrictColour {
        final int rgb;

        StrictRgb(String name, int rgb) {
            super(name);
            this.rgb = rgb;
        }

        @Override
        public boolean equals(Object other) {
            return other != null && other.getClass() == getClass()
                    && ((StrictRgb) other).rgb == rgb && name.equals(((StrictRgb) other).name);
        }

        @Override
        public int hashCode() {
            return name.hashCode() * 31 + rgb;
        }
    }

    static void report(String title, Object parent, Object child) {
        boolean up = parent.equals(child);
        boolean down = child.equals(parent);
        System.out.println(title);
        System.out.println("  parent.equals(child): " + up);
        System.out.println("  child.equals(parent): " + down);
        System.out.println("  symmetric: " + (up == down));
    }

    public static void main(String[] args) {
        report("instanceof, which lets a subclass in:",
                new Colour("teal"), new Rgb("teal", 0x008080));
        report("getClass(), which does not:",
                new StrictColour("teal"), new StrictRgb("teal", 0x008080));
    }
}
