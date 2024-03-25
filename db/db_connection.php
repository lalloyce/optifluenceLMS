<?php
    $servername = "localhost"; // replace with your server name
    $username = "root"; // replace with your username
    $password = 'D#FR$GG#D'; // replace with your password
    $dbname = "optiflow"; // replace with your database name

    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
?>