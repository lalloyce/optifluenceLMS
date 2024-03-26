<?php
// create_loan.php

// Include the database connection file
require_once __DIR__ . '/db/db_connection.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $borrower_id = $_POST['borrower_id'];
    $loan_amount = $_POST['loan_amount'];
    $loan_date = $_POST['loan_date'];
    $loan_due_date = $_POST['loan_due_date'];

    // Server-side validation
    if ($loan_amount < 5000) {
        die('Loan amount cannot be less than 5,000.');
    }

    // Calculate loan details
    $interest = $loan_amount * 0.1;
    $repayment_amount = $loan_amount + $interest;

    // Insert loan into database
    $sql = "INSERT INTO loans (borrower_id, loan_amount, interest_rate, loan_period, loan_date, loan_due_date, loan_repayment_amount, loan_balance)
            VALUES (?, ?, 10, 30, ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("iisssss", $borrower_id, $loan_amount, $loan_date, $loan_due_date, $repayment_amount, $repayment_amount);

    if ($stmt->execute()) {
        echo 'Loan created successfully.';
    } else {
        echo 'Failed to create loan.';
    }

    $stmt->close();
    $conn->close();
}
?>