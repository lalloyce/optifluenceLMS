<?php

    // Include the database connection file
    require_once __DIR__ . '/config/db.php';

    // Query the database
    $result = $conn->query("SELECT * FROM your_table");

    // Fetch all of the remaining rows in the result set
    $data = $result->fetch_all(MYSQLI_ASSOC);

    // Output the data in JSON format
    echo json_encode($data);
?>