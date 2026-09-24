public class Sol1 {
    static final class Rectangle {
        private final int width;
        private final int height;

        Rectangle(int width, int height) {
            if (width <= 0 || height <= 0) {
                throw new IllegalArgumentException("sides must be positive: " + width + " x " + height);
            }
            this.width = width;
            this.height = height;
        }

        int width() {
            return width;
        }

        int height() {
            return height;
        }

        int area() {
            return width * height;
        }

        int perimeter() {
            return 2 * (width + height);
        }

        boolean isSquare() {
            return width == height;
        }

        @Override
        public String toString() {
            return width + "x" + height;
        }
    }

    public static void main(String[] args) {
        Rectangle square = new Rectangle(4, 4);
        Rectangle oblong = new Rectangle(4, 6);

        System.out.println(square + " area " + square.area()
                + ", perimeter " + square.perimeter() + ", square: " + square.isSquare());
        System.out.println(oblong + " area " + oblong.area()
                + ", perimeter " + oblong.perimeter() + ", square: " + oblong.isSquare());

        try {
            new Rectangle(0, 5);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
        System.out.println("there is no setter, so the sides cannot change after construction");
    }
}
