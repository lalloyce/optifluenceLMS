<?php
// Start the session if not already started (remove if session started elsewhere)
session_start();

    // Turn on all error reporting
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    // Include the database connection file
    require_once __DIR__ . '/config/db.php';

// Check if form is submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Validate input (You can add more validation as per your requirements)
    if (!empty($username) && !empty($password)) {
        // Prepare statement
        $stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        // Fetch user
        if ($result->num_rows == 1) {
            $user = $result->fetch_assoc();
            // Verify password
            if (password_verify($password, $user['password'])) {
                // Password is correct, log in the user
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                // Redirect to dashboard or any other page upon successful login
                header('Location: dashboard.html');
                exit;
            } else {
                // Invalid password
                $error = "Invalid username or password";
            }
        } else {
            // Invalid username
            $error = "Invalid username or password";
        }
    } else {
        // Both fields are required
        $error = "Both username and password are required";
    }
}
?>
