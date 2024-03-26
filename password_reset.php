<?php
// Start the session
session_start();

// Include the database connection file
require_once __DIR__ . '/scripts/db.php';

// Check if form is submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];

    // Check if username exists
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        // Username exists, generate and send password reset link
        // Your code to handle password reset goes here
        $success = "Password reset link sent to your email";
    } else {
        // Username doesn't exist
        $error = "Username does not exist";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Password Reset</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>

<h2>Password Reset</h2>
<form action="scripts/password_reset.php" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required><br>
    <button type="submit">Reset Password</button>
</form>
<?php if(isset($error)) echo "<p>$error</p>"; ?>
<?php if(isset($success)) echo "<p>$success</p>"; ?>

</body>
</html>
