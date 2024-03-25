<?php
session_start();

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require 'db/db_connection.php';
$error = '';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $input_username = trim($_POST["username"]);
    $input_password = trim($_POST["password"]);

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        error_log("Connection failed: " . $conn->connect_error);
        die("Connection failed. Please try again later.");
    }

    $sql = "SELECT * FROM users WHERE username = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $input_username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        if (password_verify($input_password, $user['password'])) {
            // Reset login attempts
            $sql = "UPDATE users SET login_attempts = 0 WHERE username = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("s", $input_username);
            $stmt->execute();

            $_SESSION['username'] = $user['username'];
            header("Location: dashboard.php");
            exit();
        } else {
            // Increment login attempts
            $sql = "UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("s", $input_username);
            $stmt->execute();

            // Check if login attempts exceed limit
            if ($user['login_attempts'] + 1 > 3) {
                die("Too many failed login attempts. Please try again later.");
            } else {
                $error = 'Invalid password.';
            }
        }
    } else {
        $error = 'Invalid username.';
    }

    $stmt->close();
    $conn->close();
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
    <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <input type="submit" value="Login">
        <?php echo $error; ?>
    </form>
    <a href="password_reset.php" class="button">Reset Password</a>

    <footer>
        <p>&copy; <?php echo date("Y"); ?> Optifluence Limited</p>
    </footer>

</body>
</html>