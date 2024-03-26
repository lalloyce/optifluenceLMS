<?php
// fetch_borrower_details.php

// Include the database connection file
require_once __DIR__ . '/db/db_connection.php';

$input = $_GET['input'];

    // Fetch borrower details
    $sql = "SELECT nationalId, firstName, lastName FROM borrowers WHERE nationalId = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $input);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $borrower = $result->fetch_assoc();

        // Return borrower details as JSON
        echo json_encode($borrower);
    } else {
        echo json_encode([]);
    }

$stmt->close();
$conn->close();
?>