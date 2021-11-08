<?php

function display_data($data) {
  $output = "<table>";
  foreach($data as $key => $var) {
      //$output .= '<tr>';
      if($key===0) {
          $output .= '<tr>';
          foreach($var as $col => $val) {
              $output .= "<td>" . $col . '</td>';
          }
          $output .= '</tr>';
          foreach($var as $col => $val) {
              $output .= '<td>' . $val . '</td>';
          }
          $output .= '</tr>';
      }
      else {
          $output .= '<tr>';
          foreach($var as $col => $val) {
              $output .= '<td>' . $val . '</td>';
          }
          $output .= '</tr>';
      }
  }
  $output .= '</table>';
  echo $output;
}
require_once("password.php");
//echo password_hash("sup3rAdm1n",PASSWORD_BCRYPT_DEFAULT_COST);
if(PasswordCompat\binary\check()){
echo "oui";
}else { echo "non";}

define('DB_SERVER', 'ctfd_db');
define('DB_USERNAME', 'ctfd');
define('DB_PASSWORD', 'ctfd');
define('DB_NAME', 'ctfd');

/* Attempt to connect to MySQL database */
$conn = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);
 

$sql="select * from users ";
$result=$conn->query($sql);
if ($result->num_rows > 0) {
  display_data($result->fetch_all(MYSQLI_ASSOC));
  // output data of each row
  /*while($row = $result->fetch_assoc()) {
    echo implode(" / ",$row);
    echo "</br>";
  }*/
} else {
  echo "0 results";
}
$conn->close();
?>