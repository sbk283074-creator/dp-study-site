import java.sql.SQLException;

public class BadCatch {
    public static void main(String[] args) {
        try {
            System.out.println("nothing in this block can throw SQLException");
        } catch (SQLException e) {
            System.out.println("never happens");
        }
    }
}
