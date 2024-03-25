<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require 'db/db_connection.php';
if (file_exists(__DIR__ . '/vendor/autoload.php')) {
    require_once __DIR__ . '/vendor/autoload.php';
} else {
    die('The autoload.php file does not exist in the vendor directory.');
}
require 'email_connection.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $input_username = trim($_POST["username"]);
    $input_password = trim($_POST["password"]);
    $input_confirm_password = trim($_POST["confirm_password"]);

    if($input_password !== $input_confirm_password) {
        die('Password and Confirm password should match.');
    }

    // Check password strength
    $uppercase = preg_match('@[A-Z]@', $input_password);
    $lowercase = preg_match('@[a-z]@', $input_password);
    $number    = preg_match('@[0-9]@', $input_password);
    $specialChars = preg_match('@[^\w]@', $input_password);

    if(!$uppercase || !$lowercase || !$number || !$specialChars || strlen($input_password) < 8) {
        die('Password should be at least 8 characters in length and should include at least one upper case letter, one number, and one special character.');
    } else {
        $input_password = password_hash($input_password, PASSWORD_DEFAULT);
    }

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

        // Check if more than 1 hour has passed
        if ($now->getTimestamp() - $reset_requested_at->getTimestamp() > 60 * 60) {
            die("Reset link has expired. Please request a new one.");
        }

        $sql = "UPDATE users SET password = ?, reset_requested_at = ? WHERE username = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("sss", $input_password, $now->format('Y-m-d H:i:s'), $input_username);
        $stmt->execute();

        // Create a new PHPMailer instance
        $mail = new PHPMailer(true);

        try {
            // Server settings
            $mail->SMTPDebug = 0;
            $mail->isSMTP();
            $mail->Host       = $email_host;
            $mail->SMTPAuth   = true;
            $mail->Username   = $email_username;
            $mail->Password   = $email_password;
            $mail->SMTPSecure = $email_SMTPSecure;
            $mail->Port       = $email_port;

            // Recipients
            $mail->setFrom($email_username, 'Mailer');
            $mail->addAddress($user['email'], $input_username);

            // Content
            $mail->isHTML(true);
            $mail->Subject = 'Password Reset Successful';
            $mail->Body    = 'Your password has been reset successfully.';

            $mail->send();
            echo 'Message has been sent';
        } catch (Exception $e) {
            echo "Message could not be sent. Mailer Error: {$mail->ErrorInfo}";
        }

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
        <label for="confirm_password">Confirm New Password:</label>
        <input type="password" id="confirm_password" name="confirm_password" required>
        <input type="submit" value="Reset Password">
    </form>

    <footer>
        <p>&copy; <?php echo date("Y"); ?> Optifluence Limited</p>
    </footer>

</body>
</html>