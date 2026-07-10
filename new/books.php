<?php 
require 'config.php';
if(!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

if(isset($_GET['add']) && isset($_GET['book_id'])) {
    $book_id = (int)$_GET['book_id'];
    $user_id = $_SESSION['user_id'];
    
    $stmt = $pdo->prepare("INSERT IGNORE INTO wishlist (user_id, book_id) VALUES (?, ?)");
    $stmt->execute([$user_id, $book_id]);
    
    header("Location: books.php?success=added_to_wishlist");
    exit;
}

if(isset($_POST['add_book'])) {
    $title = trim($_POST['title']);
    $author = trim($_POST['author']);
    $description = trim($_POST['description']);

    if(!empty($title) && !empty($author)) {
        $stmt = $pdo->prepare("INSERT INTO books (title, author, description) VALUES (?, ?, ?)");
        $stmt->execute([$title, $author, $description]);
        $success = "✅ New book added successfully!";
    } else {
        $error = "Title and Author are required!";
    }
}

if(isset($_GET['delete'])) {
    $id = (int)$_GET['delete'];
    $stmt = $pdo->prepare("DELETE FROM books WHERE id = ?");
    $stmt->execute([$id]);
    header("Location: books.php?success=deleted");
    exit;
}

if(isset($_POST['update_book'])) {
    $id = (int)$_POST['book_id'];
    $title = trim($_POST['title']);
    $author = trim($_POST['author']);
    $description = trim($_POST['description']);

    if(!empty($title) && !empty($author)) {
        $stmt = $pdo->prepare("UPDATE books SET title=?, author=?, description=? WHERE id=?");
        $stmt->execute([$title, $author, $description, $id]);
        header("Location: books.php?success=updated");
        exit;
    }
}

$edit_book = null;
if(isset($_GET['edit'])) {
    $id = (int)$_GET['edit'];
    $stmt = $pdo->prepare("SELECT * FROM books WHERE id = ?");
    $stmt->execute([$id]);
    $edit_book = $stmt->fetch();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Books - BookHaven</title>
    <link rel="stylesheet" href="assets/style.css">
    <style>
        .form-control {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }
        .action-buttons {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }
        .success-msg { color: green; font-weight: bold; }
        .error-msg { color: red; font-weight: bold; }
    </style>
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
        <h1 style="text-align:center; margin-bottom:2rem; color:#2c1810;">📚 Manage Books</h1>

        <?php if(isset($success)): ?>
            <p class="success-msg" style="text-align:center;"><?= $success ?></p>
        <?php endif; ?>
        <?php if(isset($error)): ?>
            <p class="error-msg" style="text-align:center;"><?= $error ?></p>
        <?php endif; ?>

        <?php if(isset($_GET['success'])): ?>
            <p class="success-msg" style="text-align:center;">
                <?php
                if($_GET['success'] == 'added_to_wishlist') echo '✅ Book added to your Wishlist!';
                elseif($_GET['success'] == 'deleted') echo '✅ Book deleted successfully!';
                elseif($_GET['success'] == 'updated') echo '✅ Book updated successfully!';
                ?>
            </p>
        <?php endif; ?>

        <div class="card">
            <h2><?= $edit_book ? 'Edit Book' : 'Add New Book' ?></h2>
            <form method="POST">
                <?php if($edit_book): ?>
                    <input type="hidden" name="book_id" value="<?= $edit_book['id'] ?>">
                <?php endif; ?>

                <input type="text" name="title" class="form-control" 
                       placeholder="Book Title" 
                       value="<?= htmlspecialchars($edit_book['title'] ?? '') ?>" required>

                <input type="text" name="author" class="form-control" 
                       placeholder="Author Name" 
                       value="<?= htmlspecialchars($edit_book['author'] ?? '') ?>" required>

                <textarea name="description" class="form-control" rows="4" 
                          placeholder="Book Description"><?= htmlspecialchars($edit_book['description'] ?? '') ?></textarea>

                <button type="submit" name="<?= $edit_book ? 'update_book' : 'add_book' ?>" 
                        class="btn btn-primary" style="width:100%; padding:14px; font-size:1.1rem;">
                    <?= $edit_book ? 'Update Book' : 'Add Book' ?>
                </button>

                <?php if($edit_book): ?>
                    <a href="books.php" style="display:block; text-align:center; margin-top:12px; color:#666;">Cancel Edit</a>
                <?php endif; ?>
            </form>
        </div>

        <h2 style="margin: 2.5rem 0 1.5rem;">All Books</h2>
        <div class="book-grid">
            <?php
            $stmt = $pdo->query("SELECT * FROM books ORDER BY title ASC");
            while($book = $stmt->fetch()) {
                $img_id = ($book['id'] == 5) ? 1015 : (100 + $book['id']); 
                
                echo "
                <div class='book-card'>
                    <img src='https://picsum.photos/id/{$img_id}/300/240' alt='{$book['title']}'>
                    <div class='book-info'>
                        <h3>{$book['title']}</h3>
                        <p><strong>By:</strong> {$book['author']}</p>
                        <p style='margin:10px 0 15px; font-size:0.95rem; color:#555; flex:1;'>{$book['description']}</p>
                        
                        <div class='action-buttons'>
                            <a href='books.php?edit={$book['id']}' class='btn btn-edit'>Edit</a>
                            <a href='books.php?delete={$book['id']}' 
                               onclick=\"return confirm('Delete this book permanently?')\" 
                               class='btn btn-delete'>Delete</a>
                        </div>
                        <a href='books.php?add=1&book_id={$book['id']}' class='btn btn-primary'>Add to Wishlist</a>
                    </div>
                </div>";
            }
            ?>
        </div>
    </div>

    <footer>
        &copy; <?= date("Y") ?> BookHaven - All Rights Reserved | Student Project Joel Nelson (113021135)
    </footer>
</body>
</html>
