<?php
    // logout.php

    // Start or resume the session
    session_start();

    // Unset all of the session variables
    session_unset();

    // Destroy the session
    session_destroy();

    // Redirect to index.html
    header('Location: /../index.html');
    exit;
?>