<?php
    // Start the session
    session_start();

    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);

    /*
    // Check if the user is not logged in
    if (!isset($_SESSION['username'])) {
        // Redirect the user to the login page
        header("Location: index.php");
        exit();
    }

    // Check if the success message session variable is set
    if (isset($_SESSION['success_message'])) {
        // Display the success message
        echo '<div class="alert alert-success">' . $_SESSION['success_message'] . '</div>';

        // Unset the session variable
        unset($_SESSION['success_message']);
    }
    */
?>

<html>
    <head>
        <title>Dashboard</title>
        <link rel="stylesheet" type="text/css" href="styles.css">
        <!-- Header section -->
        <div class="header">
            <img src="images/logo.png" alt="Logo">
        </div>

        <!-- Navigation bar -->
        <nav>
            <ul>
                <li><a href="dashboard.php">Home</a></li>
                <li><a href="create_member.html">Create New Member</a></li>
                <li><a href="create_loan.html">Create New Loan</a></li>
                <!-- Add a dropdown menu -->
                <li>
                    <a href="#">Reports</a>
                    <div class="dropdown-menu">
                        <a href="#">Repaid Loans</a>
                        <a href="#">Overdue Loans</a>
                        <a href="#">All Loans</a>
                        <a href="#">All Members</a>
                    </div>
                </li>
                <!-- Add more navigation links as needed -->
            </ul>
        </nav>
    </head>
    <body>
        <!-- Main content container -->
        <div class="container">
            <h1>Dashboard</h1>
            <p>Welcome to the dashboard!</p>
        </div>
    </body>
</html>