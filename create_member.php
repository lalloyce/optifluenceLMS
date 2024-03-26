<?php
    //Start the session
    session_start();

    // Include the database connection file
   require_once __DIR__ . '/db/db_connection.php';

    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $firstName = $_POST['firstName'];
    $lastName = $_POST['lastName'];
    $dob = $_POST['dob'];
    $nationalId = $_POST['nationalId'];
    $location = $_POST['location'];
    $occupation = $_POST['occupation'];
    $city = $_POST['city'];
    $county = $_POST['county'];
    $mobileNumber = $_POST['mobileNumber'];
    $email = $_POST['email'];

    // Server-side validation
    if (strlen($nationalId) !== 8 || !is_numeric($nationalId)) {
        die('National ID must be 8 digits.');
    }

    if (strlen($mobileNumber) !== 10 || !is_numeric($mobileNumber)) {
        die('Mobile number must be 10 digits.');
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        die('Please enter a valid email address.');
    }

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die('Connection failed: ' . $conn->connect_error);
    }

    $sql = "INSERT INTO borrowers (firstName, lastName, dob, nationalId, location, occupation, city, county, mobileNumber, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssssssssss", $firstName, $lastName, $dob, $nationalId, $location, $occupation, $city, $county, $mobileNumber, $email);

    if ($stmt->execute()) {
        $_SESSION['message'] = 'Borrower added successfully.';
        header('Location: index.php');
    } else {
        $_SESSION['message'] = 'Failed to add borrower.';
        header('Location: index.php');
    }

    $stmt->close();
    $conn->close();
}
?>