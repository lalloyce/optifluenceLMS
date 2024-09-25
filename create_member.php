<?php
    // Start the session
    session_start();

    // Include the database connection file
    require_once __DIR__ . '/../config/db.php'

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

    // Check if borrower already exists
    $checkSql = "SELECT * FROM borrowers WHERE nationalId = ?";
    $checkStmt = $conn->prepare($checkSql);
    $checkStmt->bind_param("s", $nationalId);
    $checkStmt->execute();
    $checkResult = $checkStmt->get_result();

    if ($checkResult->num_rows > 0) {
        $_SESSION['message'] = 'Borrower with this National ID already exists.';
        header('Location: dashboard.html');
        exit();
    }

    $checkStmt->close();

    $sql = "INSERT INTO borrowers (firstName, lastName, dob, nationalId, location, occupation, city, county, mobileNumber, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssssssssss", $firstName, $lastName, $dob, $nationalId, $location, $occupation, $city, $county, $mobileNumber, $email);

    if ($stmt->execute()) {
        $_SESSION['message'] = 'Borrower added successfully.';
        header('Location: dashboard.html');
    } else {
        $_SESSION['message'] = 'Failed to add borrower.';
        header('Location: dashboard.html');
    }

    $stmt->close();
    $conn->close();
}
?>