<?php 
require 'config.php';

if(isset($_POST['login'])) {
    $email = $_POST['email'];
    $pass = $_POST['password'];

    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch();

    if($user && password_verify($pass, $user['password'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['full_name'] = $user['full_name'];
        header("Location: index.php");
        exit;
    } else {
        $error = "Invalid email or password!";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - BookHaven</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container" style="max-width:500px; margin-top:100px;">
        <div class="card">
            <h2 style="text-align:center;">Login to BookHaven</h2>
            <?php if(isset($error)) echo "<p style='color:red;text-align:center;'>$error</p>"; ?>
            <?php if(isset($_GET['success'])) echo "<p style='color:green;text-align:center;'>Registration successful! Please login.</p>"; ?>
            
            <form method="POST">
                <input type="email" name="email" placeholder="Email" required class="card" style="width:100%; padding:12px; margin:10px 0;">
                <input type="password" name="password" placeholder="Password" required class="card" style="width:100%; padding:12px; margin:10px 0;">
                <button type="submit" name="login" class="btn btn-primary" style="width:100%; padding:12px;">Login</button>
            </form>
            <p style="text-align:center; margin-top:15px;">Don't have account? <a href="register.php">Register</a></p>
        </div>
    </div>
</body>
</html>