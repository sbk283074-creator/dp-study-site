import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class UnusedResource {
    public static void main(String[] args) throws SQLException {
        try (Connection connection = DriverManager.getConnection("jdbc:sqlite:bulletin.db")) {
            System.out.println("the connection is held but never used");
        }
    }
}
