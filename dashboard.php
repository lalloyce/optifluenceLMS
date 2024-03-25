<?php

/*
// Check if the user is not logged in
if (!isset($_SESSION['username'])) {
    // Redirect the user to the login page
    header("Location: index.php");
    exit();
}
*/
?>

    <html>
            <head>
                <title>Dashboard</title>
                <link rel="stylesheet" type="text/css" href="styles.css">
                <div class="header">
                    <img src="images/logo.png" alt="Logo">
                </div>

                <nav>
                    <ul>
                        <li><a href="dashboard.php">Home</a></li>
                        <li><a href="#" onclick="showNewMemberForm()">Create New Member</a></li>
                        <li><a href="Loans">Create New Loan</a></li>
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
                <div class="container">
                    <h1>Dashboard</h1>
                    <p>Welcome to the dashboard!</p>
                </div>
                <div id="newMemberFormContainer" style="display: none;">
                    function showNewMemberForm() {
                        document.getElementById('newMemberFormContainer').style.display = 'block';
                    }
                </div>

            </body>
        </html>