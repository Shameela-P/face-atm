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
<html lang="en-US" class="no-js">
<head>
<title>Smart ATM</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel='stylesheet' href='assets/css/bootstrap.min.css' type='text/css' media='all'/>
<link rel='stylesheet' href='assets/css/animate.min.css' type='text/css' media='all'/>
<link rel='stylesheet' href='style.css' type='text/css' media='all'/>

<link rel='stylesheet' href='icons/elegantline/style.css' type='text/css' media='all'/>
<link rel='stylesheet' href='assets/css/font-awesome.min.css' type='text/css' media='all' />
<link rel='stylesheet' href='assets/css/flexslider.css' type='text/css' media='all'/>
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
<body class="frontpage">

<header id="header">
<div id="mega-menu" class="header header2 header-sticky primary-menu icons-no default-skin zoomIn align-right">
	<nav class="navbar navbar-default redq">
	<div class="container">
		<div class="navbar-header">
			<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar">
			<span class="sr-only">Toggle navigation</span>
			<span class="icon-bar"></span>
			<span class="icon-bar"></span>
			<span class="icon-bar"></span>
			</button>
			<a class="navbar-brand" href="">
			<img src="assets/img/logo-dark.png" alt="logo">
			</a>
		</div>
		<div class="collapse navbar-collapse" id="navbar">
			<a class="mobile-menu-close"><i class="fa fa-close"></i></a>
			<div class="menu-top-menu-container">
				<ul id="menu-top-menu" class="nav navbar-nav nav-list">
					<li><a href="">Home</a></li>
					
					
				</ul>
			</div>
		</div>
		<!-- /.navbar-collapse -->
	</div>
	<!-- /.container -->
	</nav>
</div>
</header>	

<section id="home" style="padding:90px 0; background-color:#00D9D9; background-position: center; background-repeat: no-repeat;background-size: cover;background-attachment:fixed;">
	<div class="container">
		<div class="textwidget">
			<h1 class="toptitle">Verification <br/><br/><!--<i class="fa fa-star roundicon"></i>-->
			</h1>								
			<div class="contactstyle topform">										
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
</section>

<section id="about" class="whitetext" style="padding:60px;background-color:#50dcc9;" >
	<div class="container">
		<div class="so-widget-sow-headline">
			<div class="sow-headline">
				<h1 class="whitetext">SMART ATM</h1>
			</div>
		</div>
		<br/>
		
							
	</div>
</section>



<footer id="footer" class="footer2">
	<div class="copyright">
		<div class="container">
			<div class="row">
				<div class="col-md-6">
					<small>
					Smart ATM <a href="https://www.wowthemes.net/">
							 
							</a>
					</small>
				</div>
				<div class="col-md-6 text-right">
					<div class="footer-menu">
						<ul id="menu-footer-links" class="menu">
							<li><a href="#"><i class="fa fa-facebook"></i> Like us on Facebook</a></li>
							<li><a href="#"><i class="fa fa-twitter"></i> Follow us on Twitter</a></li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</div>
</footer>

<!-- SCRIPTS
================================================== -->
<script src="assets/js/jquery.js"></script>
<script src="assets/js/plugins.js"></script>


</body>
</html>