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
                        <li><a href="Members">Members</a></li>
                        <li><a href="Loans">Loans</a></li>
                        <li><a href="Reports">Reports</a></li>
                        <!-- Add a dropdown menu -->
                        <li>
                            <a href="#">Dropdown</a>
                            <div class="dropdown-menu">
                                <a href="#">Link 1</a>
                                <a href="#">Link 2</a>
                                <a href="#">Link 3</a>
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
            </body>
        </html>