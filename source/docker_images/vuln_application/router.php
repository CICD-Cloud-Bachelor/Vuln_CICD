<?php

if (isset($_GET['page'])) {
    if ($_GET['page'] === 'admin') {
        include 'admin/admin.php';
    } elseif ($_GET['page'] === 'logs') {
        include 'admin/logs.php';
    } else {
        echo "Page not found.";
    }
} else {
    echo "No page selected.";
}
