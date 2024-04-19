<?php

function sanitize_input($data) {
    return htmlspecialchars(stripslashes(trim($data)));
}

function is_logged_in() {
    return isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true;
}
?>
