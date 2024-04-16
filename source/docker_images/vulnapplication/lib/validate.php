<?php
function validate_command($command) {

    $allowedTasks = ['Task1', 'Task2', 'Task3'];
    foreach ($allowedTasks as $task) {
        if (strpos($command, $task) === 0) {
            return true; 
        }
    }
    return false; 
}

function check_admin() {
    return true;
}
