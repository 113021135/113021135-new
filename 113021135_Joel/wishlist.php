<?php 
require 'config.php';
if(!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

if(isset($_GET['remove'])) {
    $id = (int)$_GET['remove'];
    $stmt = $pdo->prepare("DELETE FROM wishlist WHERE id = ? AND user_id = ?");
    $stmt->execute([$id, $_SESSION['user_id']]);
    header("Location: wishlist.php?success=removed");
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Wishlist - BookHaven</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>

    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">📖 BookHaven</div>
            <div class="nav-links">
                <a href="index.php">Home</a>
                <a href="books.php">Browse Books</a>
                <a href="wishlist.php">My Wishlist</a>
                <a href="logout.php">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <h1 style="text-align:center; margin-bottom:2rem; color:#2c1810;">❤️ My Wishlist</h1>

        <?php if(isset($_GET['success']) && $_GET['success'] == 'removed'): ?>
            <p style="text-align:center; color:green; font-weight:bold;">✅ Book removed from wishlist</p>
        <?php endif; ?>

        <div class="book-grid">
            <?php
            $stmt = $pdo->prepare("
                SELECT w.id as wid, b.* 
                FROM wishlist w 
                JOIN books b ON w.book_id = b.id 
                WHERE w.user_id = ?
                ORDER BY b.title ASC
            ");
            $stmt->execute([$_SESSION['user_id']]);
            
            if($stmt->rowCount() == 0) {
                echo "<p style='text-align:center; grid-column:1/-1; font-size:1.3rem; padding:50px;'>Your wishlist is empty.<br><a href='books.php'>Browse Books</a></p>";
            }

            while($book = $stmt->fetch()) {
                $img_id = ($book['id'] == 5) ? 1015 : (100 + $book['id']); 
                
                echo "
                <div class='book-card'>
                    <img src='https://picsum.photos/id/{$img_id}/300/240' alt='{$book['title']}'>
                    <div class='book-info'>
                        <h3>{$book['title']}</h3>
                        <p><strong>By:</strong> {$book['author']}</p>
                        <p style='margin:10px 0 15px; font-size:0.95rem; color:#555; flex:1;'>{$book['description']}</p>
                        <a href='wishlist.php?remove={$book['wid']}' 
                           onclick=\"return confirm('Remove this book from wishlist?')\" 
                           class='btn btn-danger'>Remove</a>
                    </div>
                </div>";
            }
            ?>
        </div>
    </div>

    <footer>
        &copy; <?= date("Y") ?> BookHaven - All Rights Reserved | Student Project
    </footer>
</body>
</html>