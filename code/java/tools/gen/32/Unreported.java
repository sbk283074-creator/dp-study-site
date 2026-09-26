import java.sql.DriverManager;

public class Unreported {
    public static void main(String[] args) {
        DriverManager.getConnection("jdbc:sqlite:bulletin.db");
    }
}
