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
                <li><a href="#" onclick="showNewMemberForm()">Create New Member</a></li>
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

        <!-- New Member Form container -->
        <div id="newMemberFormContainer" style="display: none;">
            <h2>Create New Member</h2>

            <!-- New Member Form -->
            <form id="newMemberForm" action="create_member.php" method="post" class="centered-form">
                <label for="firstName">First Name:</label>
                <input type="text" id="firstName" name="firstName" required>

                <label for="lastName">Last Name:</label>
                <input type="text" id="lastName" name="lastName" required>

                <label for="dob">Date of Birth:</label>
                <input type="date" id="dob" name="dob" required>

                <label for="nationalId">National ID:</label>
                <input type="text" id="nationalId" name="nationalId" required>

                <label for="location">Physical Location:</label>
                <input type="text" id="location" name="location" required>

                <label for="occupation">Occupation:</label>
                <input type="text" id="occupation" name="occupation" required>

                <label for="city">City:</label>
                <input type="text" id="city" name="city" required>

                <label for="county">County:</label>
                <input type="text" id="county" name="county" required>

                <label for="mobileNumber">Mobile Number:</label>
                <input type="text" id="mobileNumber" name="mobileNumber" required>

                <label for="email">Email Address:</label>
                <input type="email" id="email" name="email" required>

                <input type="submit" value="Create New Member">
            </form>
        </div>
        <script>
            // Function to show the new member form
            function showNewMemberForm() {
                document.getElementById('newMemberFormContainer').style.display = 'block';