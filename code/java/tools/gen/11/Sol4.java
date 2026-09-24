import java.util.ArrayList;
import java.util.List;

public class Sol4 {

    interface Entity {
        long id();
    }

    record User(long id, String name) implements Entity {
    }

    record Order(long id, int units) implements Entity {
    }

    static final class Repo<T extends Entity> {
        private final List<T> rows = new ArrayList<>();

        void add(T row) {
            rows.add(row);
        }

        T byId(long id) {
            for (T row : rows) {
                if (row.id() == id) {
                    return row;
                }
            }
            return null;
        }

        long highestId() {
            long best = 0;
            for (T row : rows) {
                best = Math.max(best, row.id());
            }
            return best;
        }
    }

    public static void main(String[] args) {
        Repo<User> users = new Repo<>();
        users.add(new User(1, "ada"));
        users.add(new User(7, "grace"));
        System.out.println("user 7: " + users.byId(7));
        System.out.println("highest user id: " + users.highestId());

        Repo<Order> orders = new Repo<>();
        orders.add(new Order(10, 3));
        System.out.println("order 10: " + orders.byId(10));
        System.out.println("the bound lets id() be called on any T: " + users.byId(1).name());
    }
}
