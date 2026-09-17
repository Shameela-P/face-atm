<?php
/* ---------------- SAFE VARIABLE HANDLING ---------------- */
$bc     = $_REQUEST['bc'] ?? '';
$act    = $_REQUEST['act'] ?? '';
$bank   = $_POST['bank'] ?? '';
$amount = $_POST['amount'] ?? '';

/* ---------------- READ BANK LIST ---------------- */
$bs = [];
$fn3 = "upload/".$bc."_bank.txt";
if(file_exists($fn3)){
    $bk = file_get_contents($fn3);
    if($bk != ""){
        $bs = explode(",", $bk);
    }
}

/* ---------------- ACCEPT ---------------- */
if(isset($_POST['btn'])){
    file_put_contents("upload/$bc.txt", "accepted-1-0");
    header("Location: ck.php?bc=$bc&act=yes");
    exit;
}

/* ---------------- WITHDRAW ---------------- */
if(isset($_POST['btn3'])){
    if(!is_numeric($amount) || $amount <= 0){
        echo "<script>alert('Invalid Amount');</script>";
    } else {
        file_put_contents("upload/$bc.txt", "accepted-$amount-$bank");
        header("Location: ck.php?bc=$bc&act=success");
        exit;
    }
}

/* ---------------- REJECT ---------------- */
if(isset($_POST['btn2'])){
    file_put_contents("upload/$bc.txt", "2-0-0");
    header("Location: ck.php?bc=$bc&act=reject");
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ATM Customer</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- BOOTSTRAP -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- FONT AWESOME -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>
body{background:#f4f6f9;font-family:Segoe UI;}
.topmenu{background:#7a0c0c;color:#fff;padding:14px 30px;}
.sidebar{height:100vh;background:#5c0909;padding:20px;}
.sidebar a{
    background:#7a0c0c;color:#fff;padding:12px 15px;
    border-radius:10px;text-decoration:none;
    display:flex;align-items:center;gap:10px;
    margin-bottom:12px;font-weight:500;transition:.3s;
}
.sidebar a:hover{background:#ffc107;color:#000;}
.card{border-radius:15px;}
.user-img{max-width:220px;border-radius:12px;border:3px solid #dee2e6;}
.form-control{border-radius:10px;margin-bottom:15px;}
.btn{min-width:140px;font-weight:500;}
.alert{border-radius:12px;font-weight:600;}
.withdraw-box{max-width:380px;margin:auto;}

.withdraw-btn{
    font-size:18px;
    padding:14px;
    border-radius:14px;
    font-weight:600;
    letter-spacing:0.5px;
    background:linear-gradient(135deg,#0d6efd,#084298);
    border:none;
    box-shadow:0 6px 18px rgba(13,110,253,.35);
    transition:all .3s ease;
}

.withdraw-btn:hover{
    transform:translateY(-2px);
    box-shadow:0 10px 24px rgba(13,110,253,.45);
    background:linear-gradient(135deg,#084298,#0d6efd);
}

.withdraw-btn:active{
    transform:scale(.98);
}
</style>
</head>

<body>

<!-- TOP BAR -->
<div class="topmenu d-flex justify-content-between align-items-center">
    <h5 class="mb-0"><i class="fa-solid fa-gauge"></i> ATM</h5>
</div>

<div class="container-fluid">
<div class="row justify-content-center">
    <div class="col-lg-8 col-md-10">
        <div class="card shadow-sm">
            <div class="card-body p-4">

<h4 class="fw-bold mb-3">
    <i class="fa-solid fa-user"></i> Customer Approval
</h4>

<div class="card shadow-sm">
<div class="card-body p-4">

<!-- IMAGE -->
<div class="text-center mb-4">
    <img src="upload/<?php echo $bc; ?>.png" class="user-img img-thumbnail">
</div>

<!-- ACCEPT / REJECT -->
<?php if($act==""){ ?>
<form method="post" class="text-center">
    <button name="btn" class="btn btn-success me-3">
        <i class="fa fa-check"></i> Accept
    </button>
    <button name="btn2" class="btn btn-danger">
        <i class="fa fa-times"></i> Reject
    </button>
</form>
<?php } ?>

<!-- WITHDRAW FORM -->
<?php if($act=="yes"){ ?>
<form method="post" class="withdraw-box mt-4">
    <select name="bank" class="form-control" required>
        <?php
        foreach($bs as $b){
            if(trim($b)!=""){
                $x = explode("-", $b);
                if(count($x)>=2){
        ?>
        <option value="<?php echo $x[0]; ?>"><?php echo $x[1]; ?></option>
        <?php }}} ?>
    </select>

    <input type="number" name="amount" class="form-control"
           placeholder="Enter Amount"
           min="100" step="100" required>

    <button name="btn3" class="btn btn-primary withdraw-btn w-100">
    <i class="fa-solid fa-money-bill-wave me-2"></i> Withdraw Cash
</button>
</form>
<?php } ?>

<!-- STATUS -->
<?php if($act=="success"){ ?>
<div class="alert alert-success text-center mt-4">
    <i class="fa fa-check-circle"></i> Cash Withdraw Successful
</div>
<?php } ?>

<?php if($act=="reject"){ ?>
<div class="alert alert-danger text-center mt-4">
    <i class="fa fa-times-circle"></i> Transaction Rejected
</div>
<?php } ?>

</div>
</div>

</div>
</div>
</div>
</div>
</div>

</body>
</html>
