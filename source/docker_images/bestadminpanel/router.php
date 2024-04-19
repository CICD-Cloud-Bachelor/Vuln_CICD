<?php
// Determine the requested URI
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Serve the default index file for the root directory
if ($uri === '/') {
    $_SERVER['REQUEST_URI'] = '/admin/admin.php';
    include __DIR__ . '/admin/admin.php';
    return;
}

// Check if the file exists, otherwise fall back to the default index file
$path = __DIR__ . $uri;
if (file_exists($path) && !is_dir($path)) {
    return false; // Serve the requested resource as-is.
} else {
    include __DIR__ . '/admin/admin.php'; // Fallback to admin/admin.php
}
?>
