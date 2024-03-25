<?php
    // Start a new session
    session_start();

    // Check if the user is already logged in
    if (isset($_SESSION['username'])) {
        // Redirect the user to the dashboard page
        header("Location: dashboard.php");
        exit();
    }

    // Set up error logging and disable error display
    ini_set('log_errors', 1);
    ini_set('display_errors', 0);
    ini_set('display_startup_errors', 0);
    error_reporting(E_ALL);

    // Include the database connection file
    require_once __DIR__ . '/db/db_connection.php';

    // Initialize an error variable
    $error = '';

    // Check if the form is submitted
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        // Sanitize and validate the input data
        $input_username = trim($_POST["username"]);
        $input_password = trim($_POST["password"]);

    // Create a new database connection
    $conn = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);

    // Check if the database connection is successful
    if ($conn->connect_error) {
        // Log the error and display a user-friendly error message
        error_log("Connection failed: " . $conn->connect_error);
        $error = "Connection failed. Please try again later.";
    } else {
        // Prepare a SQL statement to select the user with the given username
        $sql = "SELECT * FROM users WHERE username = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $input_username);
        $stmt->execute();
        $result = $stmt->get_result();

        // Check if the user exists
        if ($result->num_rows > 0) {
            // Fetch the user data
            $user = $result->fetch_assoc();

            // Verify the password
            if (password_verify($input_password, $user['password'])) {
                // Reset login attempts
                $sql = "UPDATE users SET login_attempts = 0 WHERE username = ?";
                $stmt = $conn->prepare($sql);
                $stmt->bind_param("s", $input_username);
                $stmt->execute();

                // Store the user's data in session variables
                $_SESSION['username'] = $user['username'];

                // Redirect the user to the dashboard page
                header("Location: dashboard.php");
                exit();
            } else {
                // Increment login attempts
                $sql = "UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?";
                $stmt = $conn->prepare($sql);
                $stmt->bind_param("s", $input_username);
                $stmt->execute();

                // Check if the login attempts exceed the limit
                if ($user['login_attempts'] + 1 > 5) {
                    // Redirect the user to the password reset page
                    header("Location: password_reset.php");
                    exit();
                } else {
                    // Display an error message
                    $error = 'Invalid password.';
                }
            }
        } else {
            // Display an error message
            $error = 'Invalid username.';
        }

        // Close the statement and the database connection
        $stmt->close();
        $conn->close();
    }
}
?>

<!DOCTYPE html>
<html>
    <head>
        <title>Login | Register </title>
        <link rel="stylesheet" href="styles.css">

        <div class="header">
            <img src="images/logo.png" alt="Logo">
        </div>
    </head>

    <body>
        <!-- Login form -->
        <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <input type="submit" value="Login">
            <!-- Display the error message -->
            <?php echo $error; ?>
        </form>
        <!-- Password reset link -->
        <a href="password_reset.php" class="button">Reset Password</a>

        <footer>
            <p>&copy; <?php echo date("Y"); ?> Optifluence Limited</p>
        </footer>

    </body>
</html>