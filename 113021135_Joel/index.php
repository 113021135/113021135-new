<?php require 'config.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookHaven - Buy & Discover Books</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>

    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">📖 BookHaven</div>
            <div class="nav-links">
                <a href="index.php">Home</a>
                <a href="books.php">Browse Books</a>
                <?php if(isset($_SESSION['user_id'])): ?>
                    <a href="wishlist.php">My Wishlist</a>
                    <a href="logout.php">Logout</a>
                <?php else: ?>
                    <a href="register.php">Register</a>
                    <a href="login.php">Login</a>
                <?php endif; ?>
            </div>
        </div>
    </nav>

    <div class="hero">
        <h1>Discover Your Next Great Read</h1>
        <p>Buy, browse, and build your personal book wishlist at BookHaven</p>
    </div>

    <div class="container">
        <?php
        $pdo->query("UPDATE site_visits SET count = count + 1 WHERE id=1");
        $visits = $pdo->query("SELECT count FROM site_visits")->fetchColumn();
        ?>
        <p style="text-align:center; font-size:1.3rem; margin:1.5rem 0;">
            👥 <strong><?= number_format($visits) ?></strong> book lovers have visited
        </p>

        <div class="features">
            <div class="card">
                <h2>📅 Calendar</h2>
                <iframe src="https://calendar.google.com/calendar/embed?src=en.usa%23holiday%40group.v.calendar.google.com" 
                        style="border:0; width:100%; height:380px; border-radius:12px;" frameborder="0"></iframe>
            </div>

            <div class="card">
                <h2>📍 Our Store Location</h2>
                <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d193595.9147703055!2d-74.119763973046!3d40.69740344223377!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c24fa5d33f083b%3A0xc80b8f06e177fe62!2sNew%20York%2C%20NY%2C%20USA!5e0!3m2!1sen!2s!4v123456789" 
                        width="100%" height="380" style="border:0; border-radius:12px;" allowfullscreen="" loading="lazy"></iframe>
            </div>
        </div>
    </div>

    <footer>
        &copy; <?= date("Y") ?> BookHaven - All Rights Reserved | Student Project Joel Nelson (113021135)
    </footer>
</body>
</html>