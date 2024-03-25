<?php
$servername = "localhost";
$username = "root";
$password = 'D#FR$GG#D';
$dbname = "optiflow";

// Create connection
$link = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($link->connect_error) {
    die("Connection failed: " . $link->connect_error);
}
?>