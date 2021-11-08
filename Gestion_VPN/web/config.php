<?php
/* Database credentials. Assuming you are running MySQL
server with default setting (user 'root' with no password) */
define('DB_SERVER', 'ctfd_db');
define('DB_USERNAME', 'ctfd');
define('DB_PASSWORD', 'ctfd');
define('DB_NAME', 'ctfd');

/* Attempt to connect to MySQL database */

$conn = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);
// Check connection
if($conn === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}
?>