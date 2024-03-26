<?php
require 'db/db_connection.php';
require 'email_connection.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST["username"])) {
        // Password reset request
        $input_username = trim($_POST["username"]);

        $conn = new mysqli($servername, $username, $password, $dbname);

        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        $sql = "SELECT email FROM users WHERE username = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $input_username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $user = $result->fetch_assoc();
            $token = bin2hex(random_bytes(50)); // Create a unique token
            $now = new DateTime();

            $sql = "UPDATE users SET reset_token = ?, reset_requested_at = ? WHERE username = ?";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("sss", $token, $now->format('Y-m-d H:i:s'), $input_username);
            $stmt->execute();

            // Send an email to the user with the reset link
            $mail = new PHPMailer(true);

            try {
                $mail->SMTPDebug = 0;
                $mail->isSMTP();
                $mail->Host       = $email_host;
                $mail->SMTPAuth   = true;
                $mail->Username   = $email_username;
                $mail->Password   = $email_password;
                $mail->SMTPSecure = $email_SMTPSecure;
                $mail->Port       = $email_port;

                $mail->setFrom($email_username, 'Mailer');
                $mail->addAddress($user['email'], $input_username);

                $mail->isHTML(true);
                $mail->Subject = 'Password Reset Request';
                $mail->Body    = 'Click <a href="password_reset.php?token=' . $token . '">here</a> to reset your password.';

                $mail->send();
                echo 'Reset link has been sent to your email.';
            } catch (Exception $e) {
                echo "Message could not be sent. Mailer Error: {$mail->ErrorInfo}";
            }
        } else {
            echo "Invalid username.";
        }
    } elseif (isset($_POST["password"], $_POST["confirm_password"], $_GET["token"])) {
        // Password reset
        $input_password = trim($_POST["password"]);
        $input_confirm_password = trim($_POST["confirm_password"]);
        $token = $_GET["token"];

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

        $sql = "SELECT reset_requested_at FROM users WHERE reset_token = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $token);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $user = $result->fetch_assoc();
            $reset_requested_at = new DateTime($user['reset_requested_at']);
            $now = new DateTime();
            $interval = $reset_requested_at->diff($now);

            if ($interval->h < 1) {
                $sql = "UPDATE users SET password = ?, reset_token = NULL, reset_requested_at = NULL WHERE reset_token = ?";
                $stmt = $conn->prepare($sql);
                $stmt->bind_param("ss", $input_password, $token);
                $stmt->execute();

                echo 'Password has been reset.';
            } else {
                echo 'Reset link has expired.';
            }
        } else {
            echo "Invalid token.";
        }
        ?>