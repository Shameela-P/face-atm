<?php
extract($_REQUEST);
	define('UPLOAD_DIR', 'upload/');
	
	$f1=fopen("img.txt","r");
$r=fread($f1,filesize("img.txt"));

$filename = $bc.'.png';

$vv=$r+1;
$f2=fopen("img.txt","w");
fwrite($f2,$vv);

$fn=$bc.".txt";
$f3=fopen("upload/$fn","w");
fwrite($f3,"3-0");

	$img = $_POST['imgBase64'];
	$img = str_replace('data:image/png;base64,', '', $img);
	$img = str_replace(' ', '+', $img);
	$data = base64_decode($img);
	$file = UPLOAD_DIR . $filename; //uniqid() . '.png';
	$success = file_put_contents($file, $data);
	print $success ? $file : 'Unable to save the file.';
	
?>

