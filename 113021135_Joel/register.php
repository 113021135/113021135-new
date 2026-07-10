<?php 
require 'config.php';

if(isset($_POST['register'])) {
    $full_name = trim($_POST['full_name']);
    $email = trim($_POST['email']);
    $pass = $_POST['password'];
    $cpass = $_POST['confirm_password'];

    if(empty($full_name) || empty($email) || empty($pass)) {
        $error = "All fields are required!";
    } elseif(!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = "Invalid email format!";
    } elseif($pass !== $cpass) {
        $error = "Passwords do not match!";
    } else {
        $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$email]);
        if($stmt->rowCount() > 0) {
            $error = "Email already registered!";
        } else {
            $hashed = password_hash($pass, PASSWORD_DEFAULT);
            $stmt = $pdo->prepare("INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)");
            if($stmt->execute([$full_name, $email, $hashed])) {
                header("Location: login.php?success=registered");
                exit;
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Register - BookHaven</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container" style="max-width:500px; margin-top:100px;">
        <div class="card">
            <h2 style="text-align:center;">Create Account</h2>
            <?php if(isset($error)) echo "<p style='color:red;text-align:center;'>$error</p>"; ?>
            
            <form method="POST">
                <input type="text" name="full_name" placeholder="Full Name" required class="card" style="width:100%; padding:12px; margin:10px 0;">
                <input type="email" name="email" placeholder="Email" required class="card" style="width:100%; padding:12px; margin:10px 0;">
                <input type="password" name="password" placeholder="Password" required class="card" style="width:100%; padding:12px; margin:10px 0;">
                <input type="password" name="confirm_password" placeholder="Confirm Password" required class="card" style="width:100%; padding:12px; margin:10px 0;">
                <button type="submit" name="register" class="btn btn-primary" style="width:100%; padding:12px;">Register</button>
            </form>
            <p style="text-align:center; margin-top:15px;">Already have account? <a href="login.php">Login</a></p>
        </div>
    </div>
</body>
</html>