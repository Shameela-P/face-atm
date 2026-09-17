  <?php
extract($_REQUEST);

/*if($a=="1")
{
$f2=fopen("log.txt","w");
fwrite($f2,"1");
$msg="Accepted";
}*/
/*else if($a=="1")
{
$f2=fopen("log.txt","w");
fwrite($f2,"2");
$msg="Rejected";
}
else
{
$f2=fopen("log.txt","w");
fwrite($f2,"3");
$msg="";
}*/

$fn3=$bc."_bank.txt";
$f3=fopen("upload/$fn3","r");
$bk=fread($f3,filesize("upload/$fn3"));

$bs=array();
if($bk!="")
{
$bs=explode(",",$bk);
}

if(isset($btn))
{
$val="accept-1-0";
$fn=$bc.".txt";
$f2=fopen("upload/$fn","w");
fwrite($f2,$val);

?>
<script language="javascript">
window.location.href="ck.php?bc=<?php echo $bc; ?>&act=yes";
</script>
<?php
}
if(isset($btn3))
{
//accept
$val="accepted-".$amount."-".$bank;
$fn=$bc.".txt";
$f2=fopen("upload/$fn","w");
fwrite($f2,$val);
?>
<script language="javascript">
window.location.href="ck.php?bc=<?php echo $bc; ?>&act=success";
</script>
<?php
}
if(isset($btn2))
{
//reject
$val="2-0-0";
$fn=$bc.".txt";
$f2=fopen("upload/$fn","w");
fwrite($f2,$val);
?>
<script language="javascript">
window.location.href="ck.php?bc=<?php echo $bc; ?>&act=reject";
</script>
<?php
}
?>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ATM Customer</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- BOOTSTRAP -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- FONT AWESOME -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>
body{background:#f4f6f9;}

.topmenu{
    background:#7a0c0c;
    color:#fff;
    padding:12px 25px;
}

.sidebar{
    height:100vh;
    background:#5c0909;
    padding:20px;
}

.sidebar a{
    background:#7a0c0c;
    color:#fff;
    padding:12px;
    border-radius:8px;
    text-decoration:none;
    display:block;
    margin-bottom:10px;
    font-weight:500;
}

.sidebar a:hover{
    background:#ffc107;
    color:#000;
}
</style>
<script language="javascript">
function validate()
{
    if(document.form1.password.value=="")
    {
	alert("Enter Your Pin No.");
	document.form1.password.focus();
	return false;
	}
	if(document.form1.password.value.length!=4)
    {
	alert("Incorrect Pin No.");
	document.form1.password.select();
	return false;
	}
	return true;
}
function getpin(id)
{
var x;
x=document.form1.password.value+id;
document.form1.password.value=x;
}	
	

</script>
<style type="text/css">
<!--
.st1 {
	font-size: 24px;
	font-style: italic;
	font-weight:bold;
	color:#CCCCCC;
  text-shadow: 2px 2px 9px #ffffff;
}
.st2
{
  border-radius: 25px;
  background:#003399;
  padding: 20px;
}
.st3
{
  border-radius: 25px;
  background:#FFFFFF;
  padding: 20px;
}
.st4
{
  border-radius: 25px;
  background:#003399;
  padding: 10px;
}
.txt1
{
	color:#003366;
	font-weight:bold;
	font-family:Arial, Helvetica, sans-serif;
	font-size: 16px;
	font-variant: small-caps;

}
-->
</style>
</head>

<body>

<!-- TOP MENU -->
<div class="topmenu d-flex justify-content-between align-items-center">
    <h5 class="mb-0">
        <i class="fa-solid fa-gauge"></i>ATM
    </h5>
   <!-- <button class="btn btn-warning btn-sm">
        <i class="fa-solid fa-right-from-bracket"></i> Logout
    </button>-->
</div>

<div class="container-fluid">
<div class="row">

    <!-- SIDEBAR -->
    <div class="col-md-2 sidebar">
        <a href="">
            <i class="fa-solid fa-chart-line"></i> Dashboard
        </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-md-10 p-4">

        <!-- PAGE HEADER -->
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4 class="fw-bold mb-0">
                <i class="fa-solid fa-users"></i> Customer 
            </h4>

        
        </div>

        <!-- CUSTOMER TABLE CARD -->
        <div class="card shadow-sm">
		
<form method="post" action="" id="topcontactform">
				
				<div class="title-text">
						<p align="center"><img src="upload/<?php echo $bc; ?>.png" /></p>
						</div>
					<div class="form">
					
						
						<?php
						if($act=="")
						{
						?>
						<input name="btn" type="submit" class="btn" value="Accept">&nbsp;&nbsp;/&nbsp;&nbsp;
						<input type="submit" name="btn2" class="btn" value="Reject">
						<?php
						}
						?>
					</div>
				</form>
				<form name="form2" method="post">
						<?php
						if($act=="yes")
						{
						
						?>
						<select class="form-control" name="bank">
						<?php
						$cn=count($bs);
						$i=1;
						foreach($bs as $bs1)
						{
							if($i<$cn)
							{
						$bs2=explode("-",$bs1);
						
						?>
						<option value="<?php echo $bs2[0]; ?>"><?php echo $bs2[1]; ?></option>
						<?php
							}
						$i++;
						}
						?>
						</select>
						
						<input class="form-control main" type="text" name="amount" placeholder="Enter Amount" maxlength="5" required>
						
						<input type="submit" name="btn3" class="btn" value="Withdraw Cash">
						<?php
						}
						?>
						
						<?php
						if($act=="success")
						{
						?>
						<span style="color:#009900">Cash Withdraw Success..</span>
						<?php
						}
						if($act=="reject")
						{
						?>
						<span style="color:#FF0000">Rejected!</span>
						<?php
						}
						?>
						
						</form>

        </div>

    </div>
</div>
</div>

</body>
</html>
