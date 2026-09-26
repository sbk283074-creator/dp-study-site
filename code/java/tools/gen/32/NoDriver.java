import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Collections;

public class NoDriver {
    public static void main(String[] args) {
        System.out.println("drivers loaded : "
                + Collections.list(DriverManager.getDrivers()).size());
        try {
            DriverManager.getConnection("jdbc:sqlite:bulletin.db");
        } catch (SQLException e) {
            System.out.println("SQLException   : " + e.getMessage());
            System.out.println("SQLState       : " + e.getSQLState());
            System.out.println("vendor code    : " + e.getErrorCode());
        }
        try (Connection connection = DriverManager.getConnection("jdbc:h2:mem:bulletin")) {
            System.out.println("connected      : " + connection);
        } catch (SQLException e) {
            System.out.println("and again      : " + e.getMessage());
        }
    }
}
