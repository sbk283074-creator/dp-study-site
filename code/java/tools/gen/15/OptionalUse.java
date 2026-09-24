import java.util.Optional;

public class OptionalUse {

    record User(String name, String email) {
    }

    static Optional<String> emailOf(Optional<User> user) {
        return user.map(User::email);
    }

    public static void main(String[] args) {
        System.out.println("present user: " + emailOf(Optional.of(new User("ada", "a@x"))));
        System.out.println("no user at all: " + emailOf(Optional.empty()));

        User anonymous = new User("bob", null);
        System.out.println("a nullable field is still null, not empty: "
                + (anonymous.email() == null));
        System.out.println("and nothing in the type said so");
    }
}
