<?php
require 'db/db_connection.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $input_username = trim($_POST["username"]);
    $input_password = password_hash(trim($_POST["password"]), PASSWORD_DEFAULT);

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $sql = "SELECT reset_requested_at FROM users WHERE username = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $input_username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        $reset_requested_at = new DateTime($user['reset_requested_at']);
        $now = new DateTime();

        // Check if less than 15 minutes have passed
        if ($now->getTimestamp() - $reset_requested_at->getTimestamp() < 15 * 60) {
            die("You must wait 15 minutes between password reset requests.");
        }

        $sql = "UPDATE users SET password = ?, reset_requested_at = ? WHERE username = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("sss", $input_password, $now->format('Y-m-d H:i:s'), $input_username);
        $stmt->execute();

        header("Location: login.php");
        exit;
    } else {
        die("Invalid username.");
    }
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
</head>
<body>
    <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <label for="password">New Password:</label>
        <input type="password" id="password" name="password" required>
        <input type="submit" value="Reset Password">
    </form>
</body>
</html>