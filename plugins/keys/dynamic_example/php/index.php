<?php
error_reporting(0);
date_default_timezone_set('UTC');
function verify_key($key,$token){

//write verify code hear

return true;
}
function get_client_ip() {
    if (!empty($_SERVER["HTTP_CLIENT_IP"])) {
        $cip = $_SERVER["HTTP_CLIENT_IP"];
    } elseif (!empty($_SERVER["HTTP_X_FORWARDED_FOR"])) {
        $cip = $_SERVER["HTTP_X_FORWARDED_FOR"];
    } elseif (!empty($_SERVER["REMOTE_ADDR"])) {
        $cip = $_SERVER["REMOTE_ADDR"];
    } else {
        $cip = "Unknown";
    }
    return $cip;
}
function logprint($content) {
    // [MODIFY] have_to_change_log_file_name
    file_put_contents('errlog_13df51afc3_' . date('ymd') . '.html', date('H:i:s  ') . $content . "<br>" ,FILE_APPEND);
}
function Rec($msg) {
    global $key,$token,$auth;
    logprint(sprintf("%s=>key=%s;token=%s;auth=%s=>%s",get_client_ip(),htmlspecialchars($key),htmlspecialchars($token),htmlspecialchars($auth),htmlspecialchars($msg)));
}
$key = $_REQUEST['key'];
$token = $_REQUEST['token'];
$auth = $_REQUEST['auth'];
// [MODIFY] you can see errlog to get yourself <auth>
if($auth != 'f56b44f6d903374a0c7651c336246fbda6cef567e4458ac184eee0b441b29334'){
  header("HTTP/1.1 404 Not Found");
  Rec('ERROR_AUTH');
  exit;
}
if(strlen($token) != 32 || strlen($key) > 128){
  header("HTTP/1.1 405 Method Not Allowed");
  Rec('ERROR_PARAM');
  exit;
  
}
if(verify_key($key,$token)){ Rec('VERIFY_SUCCESS');echo 'OKAY';exit;}
Rec('VERIFY_FAIL');
header('HTTP/1.1 403 Forbidden');
exit;
?>