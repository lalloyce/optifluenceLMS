<?php
// Start the session
session_start();

// Include the database connection file
require_once __DIR__ . '/scripts/db.php';

// Check if form is submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];
    $email = $_POST['email'];

    // Validate input
    if (!empty($username) && !empty($password) && !empty($email)) {
        // Check if username or email already exists
        $stmt = $conn->prepare("SELECT * FROM users WHERE username = ? OR email = ?");
        $stmt->bind_param("ss", $username, $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            // Username or email already exists
            $error = "Username or email already exists";
        } else {
            // Hash the password
            $hashed_password = password_hash($password, PASSWORD_DEFAULT);

            // Insert new user into the database
            $stmt = $conn->prepare("INSERT INTO users (username, password, email) VALUES (?, ?, ?)");
            $stmt->bind_param("sss", $username, $hashed_password, $email);
            if ($stmt->execute()) {
                // Registration successful, redirect to login page
                header('Location: index.html');
                exit;
            } else {
                // Error inserting user
                $error = "Error registering user";
            }
        }
    } else {
        // All fields are required
        $error = "All fields are required";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Register</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>

<h2>Register</h2>
<form action="scripts/register.php" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required><br>
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required><br>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required><br>
    <button type="submit">Register</button>
</form>
<?php if(isset($error)) echo "<p>$error</p>"; ?>
<p>Already have an account? <a href="index.html">Login here</a></p>

</body>
</html>
