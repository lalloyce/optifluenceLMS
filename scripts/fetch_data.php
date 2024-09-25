<?php

    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    // Include the database connection file
    require_once '/config/db.php';

    // Query 1: Loans issued and repayments made by month
    $result1 = $conn->query("
        SELECT
            DATE_FORMAT(loans.loan_date, '%Y-%m') AS month,
            SUM(loans.loan_amount) AS total_loans,
            COALESCE(SUM(repayments.repayment_amount), 0) AS total_repayments
        FROM loans
        LEFT JOIN repayments ON DATE_FORMAT(loans.loan_date, '%Y-%m') = DATE_FORMAT(repayments.repayment_date, '%Y-%m')
        GROUP BY month
        ORDER BY month ASC
    ");

    // Query 2: Loans in default
    $result2 = $conn->query("
        SELECT
            DATE_FORMAT(loans.loan_date, '%Y-%m') AS month,
            SUM(loans.loan_amount) AS total_loans
        FROM loans
        LEFT JOIN repayments ON loans.loan_num = repayments.loan_num
        WHERE DATEDIFF(CURRENT_DATE, loans.loan_date) > 30
        GROUP BY month
        HAVING total_loans > IFNULL(SUM(repayments.repayment_amount), 0)
        ORDER BY month ASC
    ");

    // Query 3: Top borrowers
    $result3 = $conn->query("
        SELECT
            CONCAT(borrowers.firstName, ' ', borrowers.lastName) AS borrower,
            SUM(loans.loan_amount) AS total
        FROM loans
        JOIN borrowers ON loans.borrower_id = borrowers.nationalId
        GROUP BY borrower
        ORDER BY total DESC
        LIMIT 10
    ");

    // Query 4: Table of all loans with borrower names, status, dates, balance, and penalties
    $result4 = $conn->query("
    SELECT
        loans.loan_num,
        CONCAT(borrowers.firstName, ' ', borrowers.lastName) AS borrower,
        loans.loan_status,
        loans.loan_date,
        loans.due_date,
        loans.loan_amount,
        COALESCE(penalties.total_penalties, 0) AS total_penalties,
        COALESCE(repayments.total_repayments, 0) AS total_repayments,
        loans.loan_balance
    FROM loans
    JOIN borrowers ON loans.borrower_id = borrowers.nationalId
    LEFT JOIN (
        SELECT loan_num, SUM(penalty_amount) AS total_penalties
        FROM penalties
        GROUP BY loan_num
    ) penalties ON loans.loan_num = penalties.loan_num
    LEFT JOIN (
        SELECT loan_num, SUM(repayment_amount) AS total_repayments
        FROM repayments
        GROUP BY loan_num
    ) repayments ON loans.loan_num = repayments.loan_num
    ORDER BY loans.loan_date DESC
    ");

    // Check if the queries were successful
    if (!$result1 || !$result2 || !$result3 || !$result4) {
        http_response_code(500);
        die("Error executing query: " . $conn->error);
    }

    // Fetch all of the remaining rows in the result sets
    $data1 = $result1->fetch_all(MYSQLI_ASSOC);
    $data2 = $result2->fetch_all(MYSQLI_ASSOC);
    $data3 = $result3->fetch_all(MYSQLI_ASSOC);
    $data4 = $result4->fetch_all(MYSQLI_ASSOC);

    // Check if the fetch was successful
    if (!$data1 || !$data2 || !$data3 || !$data4) {
        http_response_code(500);
        die("Error fetching data: " . $conn->error);
    }

    // Output the data in JSON format
    echo json_encode([$data1, $data2, $data3, $data4]);

    // Close the connection
    $conn->close();
?>
