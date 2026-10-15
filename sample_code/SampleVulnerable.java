import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * Deliberately insecure sample for demonstrating the Code Submission Module.
 * DO NOT use this code in a real application. It is only ever compiled, never run.
 */
public class SampleVulnerable {

    private static final String PASSWORD = "admin123";   // hardcoded credential

    public ResultSet findUser(String username) throws SQLException {
        Connection connection = DriverManager.getConnection("jdbc:h2:mem:test", "admin", PASSWORD);
        Statement statement = connection.createStatement();
        String sql = "SELECT * FROM users WHERE name = '" + username + "'";   // SQL injection
        return statement.executeQuery(sql);
    }

    public boolean isAdmin(String name) {
        return name == "admin";   // reference comparison instead of equals()
    }

    public static void main(String[] args) {
        System.out.println("Sample only - not executed by the validator.");
    }
}
