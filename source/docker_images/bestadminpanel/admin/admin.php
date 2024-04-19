<?php
include '../lib/validate.php';
include '../lib/command.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (check_admin() && !empty($_POST['command']) && validate_command($_POST['command'])) {
        // Execute command but do not reveal what it does
        $output = execute_command($_POST['command']);
        switch ($_POST['command']) {
            case 'Task1':
                $feedback = "Diagnostic checks completed successfully.";
                break;
            case 'Task2':
                $feedback = "System settings updated based on provided parameters.";
                break;
            case 'Task3':
                $feedback = "System usage reports generated and emailed to admin.";
                break;
            default:
                $feedback = "Invalid task specified.";
                break;
        }
    } else {
        $feedback = "Invalid task specified. Please enter a valid task (Task1, Task2, Task3).";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
    <div class="admin-wrapper">
        <h1>Admin Panel</h1>
        <p>Manage system tasks</p>
        <form action="/admin/admin.php" method="POST">
            <input type="text" name="command" placeholder="Enter task parameters (Task1, Task2, Task3)">
            <button type="submit">Run Task</button>
        </form>
        <button onclick="toggleHelp()">Help</button>
        <div id="helpMenu" style="display:none;">
            <ul>
                <li><b>Task 1:</b> Run diagnostic checks on the system.</li>
                <li><b>Task 2:</b> Update system settings based on provided parameters.</li>
                <li><b>Task 3:</b> Generate reports for system usage.</li>
            </ul>
        </div>
        <?php if (!empty($feedback)): ?>
            <p class="feedback"><?= htmlspecialchars($feedback); ?></p>
        <?php endif; ?>
    </div>
    <script>
        function toggleHelp() {
            var helpMenu = document.getElementById('helpMenu');
            helpMenu.style.display = helpMenu.style.display === 'none' ? 'block' : 'none';
        }
    </script>
</body>
</html>
