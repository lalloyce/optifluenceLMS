<?php
        // Enable error reporting
        ini_set('display_errors', 1);
        ini_set('display_startup_errors', 1);
        error_reporting(E_ALL);

    // Database connection details
    $servername = "localhost"; // replace with your server name
    $username = "root"; // replace with your username
    $password = 'D#FR$GG#D'; // replace with your password
    $dbname = "optiflow"; // replace with your database name

    //set the database
    $dbname = "optiflow"; // replace with your database name

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Check connection
    if ($conn->connect_error) {
        http_response_code(500);
        die("Connection failed: " . $conn->connect_error);
    }

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

    // Check if the queries were successful
    if (!$result1 || !$result2 || !$result3) {
        http_response_code(500);
        die("Error executing query: " . $conn->error);
    }

    // Fetch all of the remaining rows in the result sets
    $data1 = $result1->fetch_all(MYSQLI_ASSOC);
    $data2 = $result2->fetch_all(MYSQLI_ASSOC);
    $data3 = $result3->fetch_all(MYSQLI_ASSOC);

    // Check if the fetch was successful
    if (!$data1 || !$data2 || !$data3) {
        http_response_code(500);
        die("Error fetching data: " . $conn->error);
    }

    // Output the data in JSON format
    echo json_encode([$data1, $data2, $data3]);
?>