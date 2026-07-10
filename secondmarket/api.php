<?php
header('Content-Type: application/json');
session_start();

$host = 'localhost';
$db   = 'secondhand_market';
$user = 'root';
$pass = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo json_encode(["error" => "Database connection failed: " . $e->getMessage()]);
    exit;
}

// Auto cleanup expired discounts
try {
    $pdo->query("UPDATE products SET sale_price = NULL, discount_type = 'none', discount_expires_at = NULL WHERE discount_type = 'temporary' AND discount_expires_at <= NOW()");
} catch (Exception $e) {}

// Update last active for logged-in user
function updateLastActive($pdo) {
    if(isset($_SESSION['user_id'])) {
        $stmt = $pdo->prepare("UPDATE users SET last_active = NOW() WHERE id = ?");
        $stmt->execute([$_SESSION['user_id']]);
    }
}
updateLastActive($pdo);

$action = $_GET['action'] ?? '';

// ---------- GUEST BROWSER SESSION CHECK ----------
if ($action === 'check_session') {
    if (isset($_SESSION['user_id'])) {
        echo json_encode([
            "logged_in" => true,
            "user" => [
                "id" => $_SESSION['user_id'],
                "name" => $_SESSION['full_name'],
                "role" => $_SESSION['role']
            ]
        ]);
    } else {
        echo json_encode(["logged_in" => false]);
    }
    exit;
}

// ---------- AUTH & PROFILE (Customer / Vendor) ----------
if ($action === 'login' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
    $stmt->execute([$email]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if ($user && password_verify($password, $user['password_hash'])) {
        if ($user['role'] === 'vendor' && $user['account_status'] === 'pending') {
            echo json_encode(["success" => false, "message" => "Your vendor store account is pending approval by an Admin."]);
            exit;
        }
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['role'] = $user['role'];
        $_SESSION['full_name'] = $user['full_name'];
        $up = $pdo->prepare("UPDATE users SET last_active = NOW() WHERE id = ?");
        $up->execute([$user['id']]);
        echo json_encode(["success" => true, "message" => "Welcome back!", "user" => ["name" => $user['full_name'], "email" => $user['email'], "role" => $user['role']]]);
    } else {
        echo json_encode(["success" => false, "message" => "Invalid email or password combination."]);
    }
}
elseif ($action === 'register' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    $confirmPassword = $_POST['confirmPassword'] ?? '';
    $emailPattern = '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/';
    if (!preg_match($emailPattern, $email)) { echo json_encode(["success" => false, "message" => "Invalid email format."]); exit; }
    if ($password !== $confirmPassword) { echo json_encode(["success" => false, "message" => "Passwords do not match."]); exit; }
    if (strlen($password) < 4 || strlen($password) > 12) { echo json_encode(["success" => false, "message" => "Password must be 4-12 characters."]); exit; }
    
    $role = $_POST['role'] === 'vendor' ? 'vendor' : 'customer';
    $status = ($role === 'vendor') ? 'pending' : 'approved';
    $password_hash = password_hash($password, PASSWORD_DEFAULT);
    $shop_profile_filename = 'default_shop.png';
    
    if ($role === 'vendor' && isset($_FILES['shopProfilePic']) && $_FILES['shopProfilePic']['error'] === UPLOAD_ERR_OK) {
        $fileExtension = strtolower(pathinfo($_FILES['shopProfilePic']['name'], PATHINFO_EXTENSION));
        if (in_array($fileExtension, ['jpg', 'jpeg', 'png', 'gif', 'webp'])) {
            $uploadFileDir = './uploads/';
            if (!is_dir($uploadFileDir)) { mkdir($uploadFileDir, 0755, true); }
            $shop_profile_filename = md5(time() . $_FILES['shopProfilePic']['name']) . '.' . $fileExtension;
            move_uploaded_file($_FILES['shopProfilePic']['tmp_name'], $uploadFileDir . $shop_profile_filename);
        }
    }

    $sql = "INSERT INTO users (full_name, email, password_hash, role, account_status, shop_name, shop_description, shop_profile_pic, last_active, store_rating) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW(), 0)";
    $stmt = $pdo->prepare($sql);
    try {
        $stmt->execute([
            $_POST['fullName'],
            $email,
            $password_hash,
            $role,
            $status,
            !empty($_POST['shopName']) ? $_POST['shopName'] : null,
            !empty($_POST['shopDescription']) ? $_POST['shopDescription'] : null,
            $shop_profile_filename
        ]);
        echo json_encode(["success" => true, "message" => "Registration successful! Please login."]);
    } catch (PDOException $e) {
        echo json_encode(["success" => false, "message" => "Database error: " . $e->getMessage()]);
    }
}
elseif ($action === 'update_profile' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { echo json_encode(["success"=>false, "message"=>"Not logged in"]); exit; }
    $name = $_POST['full_name'] ?? '';
    $email = $_POST['email'] ?? '';
    $stmt = $pdo->prepare("UPDATE users SET full_name = ?, email = ? WHERE id = ?");
    $stmt->execute([$name, $email, $_SESSION['user_id']]);
    $_SESSION['full_name'] = $name;
    echo json_encode(["success"=>true, "message"=>"Profile information updated successfully!"]);
}
elseif ($action === 'change_password' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { echo json_encode(["success"=>false]); exit; }
    $curr = $_POST['current_password'] ?? '';
    $new = $_POST['new_password'] ?? '';
    $stmt = $pdo->prepare("SELECT password_hash FROM users WHERE id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    $user = $stmt->fetch();
    
    if(password_verify($curr, $user['password_hash'])) {
        $hash = password_hash($new, PASSWORD_DEFAULT);
        $upd = $pdo->prepare("UPDATE users SET password_hash = ? WHERE id = ?");
        $upd->execute([$hash, $_SESSION['user_id']]);
        echo json_encode(["success"=>true, "message"=>"Password securely updated!"]);
    } else {
        echo json_encode(["success"=>false, "message"=>"Incorrect current password."]);
    }
}
elseif ($action === 'update_last_active') {
    updateLastActive($pdo);
    echo json_encode(["success" => true]);
}

// ---------- PRODUCT MANAGEMENT ----------
elseif ($action === 'get_vendor_products') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { 
        echo json_encode([]); 
        exit; 
    }
    
    try {
        $stmt = $pdo->prepare("SELECT *, TIMESTAMPDIFF(SECOND, NOW(), discount_expires_at) as expiry_seconds FROM products WHERE vendor_id = ? ORDER BY id DESC");
        $stmt->execute([$_SESSION['user_id']]);
        $products = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        foreach($products as &$p) {
            $imgStmt = $pdo->prepare("SELECT image_filename FROM product_images WHERE product_id = ? ORDER BY sort_order LIMIT 1");
            $imgStmt->execute([$p['id']]);
            $firstImg = $imgStmt->fetch(PDO::FETCH_ASSOC);
            if($firstImg) $p['product_image'] = $firstImg['image_filename'];
        }
        
        echo json_encode($products);
    } catch (Exception $e) {
        echo json_encode(["error" => "Failed to fetch products: " . $e->getMessage()]);
    }
    exit;
}
elseif ($action === 'add_product' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { echo json_encode(["success" => false, "message" => "Unauthorized"]); exit; }
    $title = $_POST['title'] ?? '';
    $description = $_POST['description'] ?? '';
    $price = $_POST['price'] ?? 0;
    
    // Supports multi-select category strings passed via the hidden input
    $category = !empty($_POST['category']) ? $_POST['category'] : 'uncategorized';
    
    $stock = intval($_POST['stock'] ?? 1);
    $sale_price = !empty($_POST['sale_price']) ? $_POST['sale_price'] : null;
    $discount_type = $_POST['discount_type'] ?? 'none';
    $discount_expires_at = null;
    if ($discount_type === 'temporary' && !empty($sale_price)) {
        $duration_value = intval($_POST['discount_duration'] ?? 0);
        $duration_unit = $_POST['discount_unit'] ?? 'hours';
        if ($duration_value > 0) {
            $unit = ($duration_unit === 'days') ? 'DAY' : 'HOUR';
            $time_stmt = $pdo->prepare("SELECT NOW() + INTERVAL ? $unit AS expiry");
            $time_stmt->execute([$duration_value]);
            $discount_expires_at = $time_stmt->fetch(PDO::FETCH_ASSOC)['expiry'];
        } else {
            $time_stmt = $pdo->query("SELECT NOW() + INTERVAL 2 HOUR AS expiry");
            $discount_expires_at = $time_stmt->fetch(PDO::FETCH_ASSOC)['expiry'];
        }
    }
    try {
        $stmt = $pdo->prepare("INSERT INTO products (vendor_id, title, description, price, sale_price, discount_type, discount_expires_at, category, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
        $stmt->execute([$_SESSION['user_id'], $title, $description, $price, $sale_price, $discount_type, $discount_expires_at, $category, $stock]);
        $product_id = $pdo->lastInsertId();
        if(isset($_FILES['product_images']) && is_array($_FILES['product_images']['name'])) {
            $uploadDir = './uploads/';
            if (!is_dir($uploadDir)) mkdir($uploadDir, 0755, true);
            $sort = 0;
            foreach($_FILES['product_images']['tmp_name'] as $idx => $tmp) {
                if($_FILES['product_images']['error'][$idx] === UPLOAD_ERR_OK && $sort < 5) {
                    $ext = strtolower(pathinfo($_FILES['product_images']['name'][$idx], PATHINFO_EXTENSION));
                    if(in_array($ext, ['jpg','jpeg','png','gif','webp'])) {
                        $filename = md5(time().$idx.uniqid()) . '.' . $ext;
                        move_uploaded_file($tmp, $uploadDir . $filename);
                        $imgStmt = $pdo->prepare("INSERT INTO product_images (product_id, image_filename, sort_order) VALUES (?, ?, ?)");
                        $imgStmt->execute([$product_id, $filename, $sort]);
                        $sort++;
                    }
                }
            }
        }
        $firstImg = $pdo->prepare("SELECT image_filename FROM product_images WHERE product_id = ? ORDER BY sort_order LIMIT 1");
        $firstImg->execute([$product_id]);
        $first = $firstImg->fetch(PDO::FETCH_ASSOC);
        if($first) {
            $upd = $pdo->prepare("UPDATE products SET product_image = ? WHERE id = ?");
            $upd->execute([$first['image_filename'], $product_id]);
        }
        echo json_encode(["success" => true, "message" => "Product added successfully!"]);
    } catch (Exception $e) { echo json_encode(["success" => false, "message" => $e->getMessage()]); }
}
elseif ($action === 'edit_product' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { echo json_encode(["success" => false, "message" => "Unauthorized"]); exit; }
    $product_id = $_POST['product_id'] ?? '';
    $title = $_POST['title'] ?? '';
    $description = $_POST['description'] ?? '';
    $price = $_POST['price'] ?? 0;
    
    // Supports multi-select category strings
    $category = !empty($_POST['category']) ? $_POST['category'] : 'uncategorized';
    
    $stock = intval($_POST['stock'] ?? 1);
    $sale_price = !empty($_POST['sale_price']) ? $_POST['sale_price'] : null;
    $discount_type = $_POST['discount_type'] ?? 'none';
    try {
        $check = $pdo->prepare("SELECT id FROM products WHERE id = ? AND vendor_id = ?");
        $check->execute([$product_id, $_SESSION['user_id']]);
        if(!$check->fetch()) { echo json_encode(["success" => false, "message" => "Product not found"]); exit; }
        $discount_expires_at = null;
        if ($discount_type === 'temporary' && !empty($sale_price)) {
            $duration_value = intval($_POST['discount_duration'] ?? 0);
            $duration_unit = $_POST['discount_unit'] ?? 'hours';
            if ($duration_value > 0) {
                $unit = ($duration_unit === 'days') ? 'DAY' : 'HOUR';
                $time_stmt = $pdo->prepare("SELECT NOW() + INTERVAL ? $unit AS expiry");
                $time_stmt->execute([$duration_value]);
                $discount_expires_at = $time_stmt->fetch(PDO::FETCH_ASSOC)['expiry'];
            } else {
                $time_stmt = $pdo->query("SELECT NOW() + INTERVAL 2 HOUR AS expiry");
                $discount_expires_at = $time_stmt->fetch(PDO::FETCH_ASSOC)['expiry'];
            }
        }
        $stmt = $pdo->prepare("UPDATE products SET title=?, description=?, price=?, sale_price=?, discount_type=?, discount_expires_at=?, category=?, stock=? WHERE id=?");
        $stmt->execute([$title, $description, $price, $sale_price, $discount_type, $discount_expires_at, $category, $stock, $product_id]);
        if(isset($_FILES['product_images']) && is_array($_FILES['product_images']['name']) && !empty($_FILES['product_images']['name'][0])) {
            $del = $pdo->prepare("DELETE FROM product_images WHERE product_id = ?");
            $del->execute([$product_id]);
            $uploadDir = './uploads/';
            $sort = 0;
            foreach($_FILES['product_images']['tmp_name'] as $idx => $tmp) {
                if($_FILES['product_images']['error'][$idx] === UPLOAD_ERR_OK && $sort < 5) {
                    $ext = strtolower(pathinfo($_FILES['product_images']['name'][$idx], PATHINFO_EXTENSION));
                    if(in_array($ext, ['jpg','jpeg','png','gif','webp'])) {
                        $filename = md5(time().$idx.uniqid()) . '.' . $ext;
                        move_uploaded_file($tmp, $uploadDir . $filename);
                        $imgStmt = $pdo->prepare("INSERT INTO product_images (product_id, image_filename, sort_order) VALUES (?, ?, ?)");
                        $imgStmt->execute([$product_id, $filename, $sort]);
                        $sort++;
                    }
                }
            }
            $first = $pdo->prepare("SELECT image_filename FROM product_images WHERE product_id = ? ORDER BY sort_order LIMIT 1");
            $first->execute([$product_id]);
            $f = $first->fetch(PDO::FETCH_ASSOC);
            if($f) {
                $upd = $pdo->prepare("UPDATE products SET product_image = ? WHERE id = ?");
                $upd->execute([$f['image_filename'], $product_id]);
            }
        }
        echo json_encode(["success" => true, "message" => "Product updated successfully!"]);
    } catch (Exception $e) { echo json_encode(["success" => false, "message" => $e->getMessage()]); }
}
elseif ($action === 'delete_product' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { echo json_encode(["success" => false, "message" => "Unauthorized"]); exit; }
    $product_id = $_POST['product_id'] ?? '';
    try {
        $stmt = $pdo->prepare("DELETE FROM products WHERE id = ? AND vendor_id = ?");
        $stmt->execute([$product_id, $_SESSION['user_id']]);
        echo json_encode(["success" => true, "message" => "Product removed."]);
    } catch (Exception $e) { echo json_encode(["success" => false, "message" => $e->getMessage()]); }
}
elseif ($action === 'get_product_images') {
    $product_id = intval($_GET['product_id'] ?? 0);
    $stmt = $pdo->prepare("SELECT image_filename FROM product_images WHERE product_id = ? ORDER BY sort_order");
    $stmt->execute([$product_id]);
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
}
elseif ($action === 'get_products') {
    $category = $_GET['category'] ?? 'all';
    $sort = $_GET['sort'] ?? 'relevance';
    $search = $_GET['search'] ?? '';

    $query = "SELECT p.*, u.shop_name, u.store_rating, u.shop_profile_pic, u.last_active, 
              TIMESTAMPDIFF(SECOND, NOW(), p.discount_expires_at) as expiry_seconds 
              FROM products p 
              JOIN users u ON p.vendor_id = u.id 
              WHERE u.account_status = 'approved'";
              
    $params = [];

    // ENHANCED FILTER LOGIC: Supports items with multiple tags using FIND_IN_SET

    if ($category !== 'all') { 
        $query .= " AND FIND_IN_SET(?, p.category) > 0"; 
        $params[] = $category; 
    }

    // Filter by search (Check Title or Description)
    if (!empty($search)) {
        $query .= " AND (p.title LIKE ? OR p.description LIKE ?)";
        $params[] = "%$search%";
        $params[] = "%$search%";
    }

    // Ordering logic
    if ($sort === 'price-low') { $query .= " ORDER BY COALESCE(p.sale_price, p.price) ASC"; }
    elseif ($sort === 'price-high') { $query .= " ORDER BY COALESCE(p.sale_price, p.price) DESC"; }
    elseif ($sort === 'most-sold') { $query .= " ORDER BY p.sales_count DESC"; }
    else { $query .= " ORDER BY p.id DESC"; }

    $stmt = $pdo->prepare($query);
    $stmt->execute($params); 
    $products = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode($products);
}
elseif ($action === 'get_product_details') {
    $product_id = intval($_GET['id'] ?? 0);
    $stmt = $pdo->prepare("SELECT p.*, u.shop_name, u.store_rating, u.shop_profile_pic, u.last_active, u.id as vendor_id, TIMESTAMPDIFF(SECOND, NOW(), p.discount_expires_at) as expiry_seconds FROM products p JOIN users u ON p.vendor_id = u.id WHERE p.id = ?");
    $stmt->execute([$product_id]);
    $product = $stmt->fetch(PDO::FETCH_ASSOC);
    if ($product) {
        echo json_encode(["success" => true, "product" => $product]);
    } else {
        echo json_encode(["success" => false, "message" => "Product not found."]);
    }
}
elseif ($action === 'get_vendor_shop') {
    $vendor_id = intval($_GET['vendor_id'] ?? 0);
    $stmt = $pdo->prepare("SELECT id, shop_name, shop_description, shop_profile_pic, store_rating, last_active FROM users WHERE id = ? AND role = 'vendor'");
    $stmt->execute([$vendor_id]);
    $vendor = $stmt->fetch(PDO::FETCH_ASSOC);
    if($vendor) {
        $lastActive = $vendor['last_active'] ? (new DateTime($vendor['last_active']))->diff(new DateTime())->i : 0;
        $vendor['last_active_text'] = $lastActive < 1 ? 'Active now' : "Active $lastActive min ago";
        echo json_encode(["success" => true, "shop_name" => $vendor['shop_name'], "shop_description" => $vendor['shop_description'], "shop_profile_pic" => $vendor['shop_profile_pic'], "store_rating" => $vendor['store_rating'], "last_active_text" => $vendor['last_active_text']]);
    } else {
        echo json_encode(["success" => false, "message" => "Vendor not found"]);
    }
}
elseif ($action === 'get_products_by_vendor') {
    $vendor_id = intval($_GET['vendor_id'] ?? 0);
    $stmt = $pdo->prepare("SELECT id, title, description, price, sale_price, discount_type, discount_expires_at, TIMESTAMPDIFF(SECOND, NOW(), discount_expires_at) as expiry_seconds, category, stock, product_image FROM products WHERE vendor_id = ? ORDER BY id DESC");
    $stmt->execute([$vendor_id]);
    $products = $stmt->fetchAll(PDO::FETCH_ASSOC);
    foreach($products as &$p) {
        $imgStmt = $pdo->prepare("SELECT image_filename FROM product_images WHERE product_id = ? ORDER BY sort_order LIMIT 1");
        $imgStmt->execute([$p['id']]);
        $img = $imgStmt->fetch(PDO::FETCH_ASSOC);
        if($img) $p['product_image'] = $img['image_filename'];
    }
    echo json_encode($products);
}

// ---------- CART ----------
elseif ($action === 'add_to_cart' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'customer') { echo json_encode(["success" => false, "message" => "Please login as a customer."]); exit; }
    $product_id = intval($_POST['product_id'] ?? 0);
    $requested_qty = intval($_POST['quantity'] ?? 1);
    if ($requested_qty < 1) $requested_qty = 1;
    $p_stmt = $pdo->prepare("SELECT stock FROM products WHERE id = ?");
    $p_stmt->execute([$product_id]);
    $prod = $p_stmt->fetch(PDO::FETCH_ASSOC);
    if (!$prod || $prod['stock'] < 1) { echo json_encode(["success" => false, "message" => "Out of stock!"]); exit; }
    $c_stmt = $pdo->prepare("SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?");
    $c_stmt->execute([$_SESSION['user_id'], $product_id]);
    $existing = $c_stmt->fetch(PDO::FETCH_ASSOC);
    if ($existing) {
        $new_total = $existing['quantity'] + $requested_qty;
        if ($new_total > $prod['stock']) { echo json_encode(["success" => false, "message" => "Exceeds stock"]); exit; }
        $upd = $pdo->prepare("UPDATE cart SET quantity = ? WHERE id = ?");
        $upd->execute([$new_total, $existing['id']]);
    } else {
        if ($requested_qty > $prod['stock']) { echo json_encode(["success" => false, "message" => "Exceeds stock"]); exit; }
        $ins = $pdo->prepare("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)");
        $ins->execute([$_SESSION['user_id'], $product_id, $requested_qty]);
    }
    echo json_encode(["success" => true, "message" => "Added to cart"]);
}
elseif ($action === 'get_cart') {
    if (!isset($_SESSION['user_id'])) { echo json_encode([]); exit; }
    $stmt = $pdo->prepare("
        SELECT 
            c.id as cart_id, 
            c.quantity, 
            p.id as product_id, 
            p.title, 
            p.price, 
            p.sale_price, 
            COALESCE(p.sale_price, p.price) AS effective_price, 
            p.product_image, 
            p.vendor_id,
            u.shop_name
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        JOIN users u ON p.vendor_id = u.id
        WHERE c.user_id = ?
    ");
    $stmt->execute([$_SESSION['user_id']]);
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
}
elseif ($action === 'remove_from_cart' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { echo json_encode(["success" => false]); exit; }
    $cart_id = intval($_POST['cart_id'] ?? 0);
    $stmt = $pdo->prepare("DELETE FROM cart WHERE id = ? AND user_id = ?");
    $stmt->execute([$cart_id, $_SESSION['user_id']]);
    echo json_encode(["success" => true]);
}
elseif ($action === 'update_cart_quantity' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $cart_id = intval($_POST['cart_id'] ?? 0);
    $change = intval($_POST['change'] ?? 0);
    
    // Check the stock limit before allowing the customer to increase the quantity
    if ($change > 0) {
        $check = $pdo->prepare("SELECT c.quantity, p.stock FROM cart c JOIN products p ON c.product_id = p.id WHERE c.id = ?");
        $check->execute([$cart_id]);
        $data = $check->fetch(PDO::FETCH_ASSOC);
        
        if ($data && ($data['quantity'] + $change > $data['stock'])) {
            echo json_encode(["success" => false, "message" => "Maximum stock reached. You cannot add more of this item."]);
            exit;
        }
    }
    
    $stmt = $pdo->prepare("UPDATE cart SET quantity = quantity + ? WHERE id = ?");
    $stmt->execute([$change, $cart_id]);
    $pdo->prepare("DELETE FROM cart WHERE quantity <= 0")->execute();
    echo json_encode(["success" => true]);
    exit;
}

// ---------- CHECKOUT / ORDERS ----------
elseif ($action === 'process_payment' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { echo json_encode(["success"=>false, "message"=>"Login required"]); exit; }
    $method = $_POST['payment_method'] ?? 'cash';
    
    // Get Cart Items
    $stmt = $pdo->prepare("SELECT c.quantity, p.id as product_id, p.vendor_id, COALESCE(p.sale_price, p.price) as effective_price, p.stock FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id = ?");
    $stmt->execute([$_SESSION['user_id']]);
    $cartItems = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    if(!$cartItems) { echo json_encode(["success"=>false, "message"=>"Cart is empty"]); exit; }
    
    $total = 0;
    foreach($cartItems as $item) {
        if ($item['stock'] < $item['quantity']) {
            echo json_encode(["success"=>false, "message"=>"Not enough stock for a product in your cart."]); exit;
        }
        $total += $item['effective_price'] * $item['quantity'];
    }
    
    try {
        $pdo->beginTransaction();
        
        // Create order
        $ordStmt = $pdo->prepare("INSERT INTO orders (customer_id, total_amount, payment_method) VALUES (?, ?, ?)");
        $ordStmt->execute([$_SESSION['user_id'], $total, $method]);
        $orderId = $pdo->lastInsertId();
        
        // Create items & deduct stock
        $itemStmt = $pdo->prepare("INSERT INTO order_items (order_id, product_id, vendor_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?, ?)");
        $stockStmt = $pdo->prepare("UPDATE products SET stock = stock - ? WHERE id = ?");
        
        foreach($cartItems as $item) {
            $itemStmt->execute([$orderId, $item['product_id'], $item['vendor_id'], $item['quantity'], $item['effective_price']]);
            $stockStmt->execute([$item['quantity'], $item['product_id']]);
        }
        
        // Clear cart
        $pdo->prepare("DELETE FROM cart WHERE user_id = ?")->execute([$_SESSION['user_id']]);
        $pdo->commit();
        
        echo json_encode(["success"=>true, "message"=>"Payment processed successfully."]);
    } catch(Exception $e) {
        $pdo->rollBack();
        echo json_encode(["success"=>false, "message"=>$e->getMessage()]);
    }
    exit;
}
elseif ($action === 'get_vendor_orders') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { echo json_encode([]); exit; }
    
    $stmt = $pdo->prepare("
        SELECT o.id as order_id, o.created_at, o.status, u.full_name as customer_name, o.customer_id,
               oi.quantity, oi.price_at_purchase, p.title, p.product_image
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN users u ON o.customer_id = u.id
        JOIN products p ON oi.product_id = p.id
        WHERE oi.vendor_id = ?
        ORDER BY o.id DESC
    ");
    $stmt->execute([$_SESSION['user_id']]);
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    $orders = [];
    foreach($rows as $row) {
        $oid = $row['order_id'];
        if(!isset($orders[$oid])) {
            $orders[$oid] = [
                'order_id' => $oid,
                'customer_id' => $row['customer_id'],
                'customer_name' => $row['customer_name'],
                'created_at' => $row['created_at'],
                'status' => $row['status'],
                'total_amount' => 0, 
                'items' => []
            ];
        }
        $line_total = $row['price_at_purchase'] * $row['quantity'];
        $orders[$oid]['total_amount'] += $line_total;
        $orders[$oid]['items'][] = [
            'title' => $row['title'],
            'quantity' => $row['quantity'],
            'price_at_purchase' => $row['price_at_purchase'],
            'product_image' => $row['product_image']
        ];
    }
    echo json_encode(array_values($orders));
    exit;
}

// ---------- RATINGS ----------
elseif ($action === 'submit_rating' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { 
        echo json_encode(["success" => false, "message" => "Please login to rate."]); 
        exit; 
    }
    
    $vendor_id = intval($_POST['vendor_id']);
    $rating = intval($_POST['rating']);
    
    // SECURITY CHECK: Did this customer actually buy from this vendor?
    $checkStmt = $pdo->prepare("
        SELECT oi.id 
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.customer_id = ? AND oi.vendor_id = ?
        LIMIT 1
    ");
    $checkStmt->execute([$_SESSION['user_id'], $vendor_id]);
    
    if (!$checkStmt->fetch()) {
        echo json_encode(["success" => false, "message" => "Oops! You can only rate stores you have successfully purchased from."]);
        exit;
    }
    
    // If they pass the check, process the rating
    $stmt = $pdo->prepare("UPDATE users SET store_rating = CASE WHEN store_rating = 0 THEN ? ELSE (store_rating + ?) / 2 END WHERE id = ?");
    $stmt->execute([$rating, $rating, $vendor_id]);
    
    echo json_encode(["success" => true, "message" => "Rating submitted!"]);
    exit;
}

// ---------- CHAT MESSAGES ----------
elseif ($action === 'send_message' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { 
        echo json_encode(["success" => false, "message" => "Not logged in"]); 
        exit; 
    }
    
    $to_user = intval($_POST['to_user_id'] ?? 0);
    $message = trim($_POST['message'] ?? '');
    $product_id = !empty($_POST['product_id']) ? intval($_POST['product_id']) : null;
    
    if(empty($message)) { 
        echo json_encode(["success" => false, "message" => "Message is empty"]); 
        exit; 
    }
    
    try {
        $stmt = $pdo->prepare("INSERT INTO messages (from_user_id, to_user_id, product_id, message, `timestamp`) VALUES (?, ?, ?, ?, NOW())");
        $stmt->execute([$_SESSION['user_id'], $to_user, $product_id, $message]);
        
        echo json_encode(["success" => true]);
    } catch (Exception $e) {
        echo json_encode(["success" => false, "message" => "DB Error: " . $e->getMessage()]);
    }
    exit;
}
elseif ($action === 'get_messages') {
    if (!isset($_SESSION['user_id'])) { echo json_encode([]); exit; }
    $with_user = intval($_GET['with_user'] ?? 0);
    $product_id = intval($_GET['product_id'] ?? 0);
    
    try {
        $stmt = $pdo->prepare("
            SELECT m.*, u.full_name as sender_name 
            FROM messages m 
            JOIN users u ON m.from_user_id = u.id 
            WHERE (m.from_user_id = ? AND m.to_user_id = ?) 
               OR (m.from_user_id = ? AND m.to_user_id = ?) 
            ORDER BY m.timestamp ASC
        ");
        $stmt->execute([$_SESSION['user_id'], $with_user, $with_user, $_SESSION['user_id']]);
        $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);
        
        $result = [];
        foreach($messages as $msg) {
            $result[] = [
                'id' => $msg['id'],
                'message' => $msg['message'],
                'timestamp' => date('c', strtotime($msg['timestamp'])), 
                'is_mine' => ($msg['from_user_id'] == $_SESSION['user_id'])
            ];
        }
        echo json_encode($result);
    } catch (Exception $e) {
        error_log("Get Messages Error: " . $e->getMessage());
        echo json_encode([]);
    }
    exit;
}
elseif ($action === 'get_conversations') {
    if (!isset($_SESSION['user_id'])) { 
        echo json_encode([]); 
        exit; 
    }
    
    try {
        $stmt = $pdo->prepare("
            SELECT 
                u.id as other_user, 
                u.full_name as name,
                (SELECT message FROM messages 
                 WHERE (from_user_id = ? AND to_user_id = u.id) 
                    OR (from_user_id = u.id AND to_user_id = ?) 
                 ORDER BY `timestamp` DESC LIMIT 1) as last_message,
                (SELECT COUNT(*) FROM messages 
                 WHERE to_user_id = ? AND from_user_id = u.id AND is_read = 0) as unread
            FROM users u
            WHERE u.id IN (
                SELECT to_user_id FROM messages WHERE from_user_id = ?
                UNION
                SELECT from_user_id FROM messages WHERE to_user_id = ?
            )
        ");
        
        $stmt->execute([
            $_SESSION['user_id'], 
            $_SESSION['user_id'], 
            $_SESSION['user_id'], 
            $_SESSION['user_id'], 
            $_SESSION['user_id']
        ]);
        
        $convs = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($convs);
    } catch (Exception $e) {
        error_log("Chat SQL Exception: " . $e->getMessage());
        echo json_encode([]); 
    }
    exit;
}
elseif ($action === 'mark_messages_read') {
    if (!isset($_SESSION['user_id'])) { echo json_encode(["success" => false]); exit; }
    $with_user = intval($_POST['with_user'] ?? 0);
    $stmt = $pdo->prepare("UPDATE messages SET is_read = 1 WHERE to_user_id = ? AND from_user_id = ?");
    $stmt->execute([$_SESSION['user_id'], $with_user]);
    echo json_encode(["success" => true]);
}
elseif ($action === 'get_unread_count') {
    if (!isset($_SESSION['user_id'])) { echo json_encode(["count" => 0]); exit; }
    $stmt = $pdo->prepare("SELECT COUNT(*) as cnt FROM messages WHERE to_user_id = ? AND is_read = 0");
    $stmt->execute([$_SESSION['user_id']]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    echo json_encode(["count" => $row['cnt']]);
}
elseif ($action === 'get_user_info') {
    $user_id = intval($_GET['user_id'] ?? 0);
    $stmt = $pdo->prepare("SELECT full_name as name FROM users WHERE id = ?");
    $stmt->execute([$user_id]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    echo json_encode($user ?: ["name" => "User"]);
}

// ---------- PRODUCT REVIEWS (Shopee-style) ----------
elseif ($action === 'submit_product_comment' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { 
        echo json_encode(["success" => false, "message" => "Please login to review."]); 
        exit; 
    }
    
    $product_id = intval($_POST['product_id']);
    $rating = intval($_POST['rating']);
    $comment = trim($_POST['comment'] ?? '');
    
    if ($rating < 1 || $rating > 5) { 
        echo json_encode(["success" => false, "message" => "Invalid star rating."]); 
        exit; 
    }
    
    try {
        $stmt = $pdo->prepare("INSERT INTO product_reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)");
        $stmt->execute([$product_id, $_SESSION['user_id'], $rating, $comment]);
        echo json_encode(["success" => true, "message" => "Review published!"]);
    } catch (Exception $e) {
        echo json_encode(["success" => false, "message" => "Failed to submit review: " . $e->getMessage()]);
    }
    exit;
}
    
elseif ($action === 'get_product_comments') {
    $product_id = intval($_GET['product_id'] ?? 0);
    $stmt = $pdo->prepare("
        SELECT pr.rating, pr.comment, pr.created_at, u.full_name 
        FROM product_reviews pr 
        JOIN users u ON pr.user_id = u.id 
        WHERE pr.product_id = ? 
        ORDER BY pr.created_at DESC
    ");
    $stmt->execute([$product_id]);
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}

// ---------- FAVORITES ----------
elseif ($action === 'toggle_favorite' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) { 
        echo json_encode(["success" => false, "message" => "Please login to add favorites."]); 
        exit; 
    }
    $product_id = intval($_POST['product_id']);
    
    // Check if already favorited
    $stmt = $pdo->prepare("SELECT id FROM favorites WHERE user_id = ? AND product_id = ?");
    $stmt->execute([$_SESSION['user_id'], $product_id]);
    
    if ($stmt->fetch()) {
        $pdo->prepare("DELETE FROM favorites WHERE user_id = ? AND product_id = ?")->execute([$_SESSION['user_id'], $product_id]);
        echo json_encode(["success" => true, "message" => "Removed from favorites."]);
    } else {
        $pdo->prepare("INSERT INTO favorites (user_id, product_id) VALUES (?, ?)")->execute([$_SESSION['user_id'], $product_id]);
        echo json_encode(["success" => true, "message" => "❤️ Added to your favorites!"]);
    }
    exit;
}
elseif ($action === 'get_favorites') {
    if (!isset($_SESSION['user_id'])) { 
        echo json_encode([]); 
        exit; 
    }
    $stmt = $pdo->prepare("
        SELECT f.product_id, p.title, p.price, p.sale_price, p.product_image, u.shop_name 
        FROM favorites f 
        JOIN products p ON f.product_id = p.id 
        JOIN users u ON p.vendor_id = u.id 
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ");
    $stmt->execute([$_SESSION['user_id']]);
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}

// ---------- VENDOR REVIEWS ----------
elseif ($action === 'get_vendor_reviews') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { 
        echo json_encode([]); 
        exit; 
    }
    
    $stmt = $pdo->prepare("
        SELECT pr.rating, pr.comment, pr.created_at, u.full_name as customer_name, p.title as product_title
        FROM product_reviews pr
        JOIN products p ON pr.product_id = p.id
        JOIN users u ON pr.user_id = u.id
        WHERE p.vendor_id = ?
        ORDER BY pr.created_at DESC
    ");
    $stmt->execute([$_SESSION['user_id']]);
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}
elseif ($action === 'logout') { 
    session_destroy(); 
    echo json_encode(["success" => true]); 
}
elseif ($action === 'update_order_status' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { 
        echo json_encode(["success" => false, "message" => "Unauthorized"]); 
        exit; 
    }
    
    $order_id = intval($_POST['order_id'] ?? 0);
    $status = $_POST['status'] ?? '';
    
    if ($order_id && $status) {
        // Security check: Ensure this vendor actually has items in this specific order
        $check = $pdo->prepare("SELECT COUNT(*) FROM order_items WHERE order_id = ? AND vendor_id = ?");
        $check->execute([$order_id, $_SESSION['user_id']]);
        
        if($check->fetchColumn() > 0) {
            $stmt = $pdo->prepare("UPDATE orders SET status = ? WHERE id = ?");
            $stmt->execute([$status, $order_id]);
            echo json_encode(["success" => true]);
        } else {
            echo json_encode(["success" => false, "message" => "Permission denied."]);
        }
    } else {
        echo json_encode(["success" => false, "message" => "Invalid data."]);
    }
    exit;
}
elseif ($action === 'get_vendor_dashboard_stats') {
    if (!isset($_SESSION['user_id']) || $_SESSION['role'] !== 'vendor') { 
        echo json_encode(["error" => "Unauthorized"]); 
        exit; 
    }
    
    $vendor_id = $_SESSION['user_id'];
    
    $stats = [
        'total_products' => 0,
        'total_orders' => 0,
        'total_sales' => 0,
        'pending_orders' => 0,
        'shipped_orders' => 0,
        'recent_orders' => []
    ];

    // 1. Get Total Products
    $stmt = $pdo->prepare("SELECT COUNT(id) FROM products WHERE vendor_id = ?");
    $stmt->execute([$vendor_id]);
    $stats['total_products'] = (int)$stmt->fetchColumn();

    // 2. Get Total Orders & Total Revenue (Sales)
    $stmt = $pdo->prepare("SELECT COUNT(DISTINCT order_id) as total_orders, SUM(quantity * price_at_purchase) as total_sales FROM order_items WHERE vendor_id = ?");
    $stmt->execute([$vendor_id]);
    $res = $stmt->fetch(PDO::FETCH_ASSOC);
    $stats['total_orders'] = (int)$res['total_orders'];
    $stats['total_sales'] = (float)$res['total_sales'];

    // 3. Get Order Summary (Calculate Pending vs Shipped)
    $stmt = $pdo->prepare("SELECT o.status, COUNT(DISTINCT o.id) as count FROM orders o JOIN order_items oi ON o.id = oi.order_id WHERE oi.vendor_id = ? GROUP BY o.status");
    $stmt->execute([$vendor_id]);
    $statuses = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    foreach ($statuses as $st) {
        $statusStr = strtolower($st['status']);
        // Assuming 'paid' or 'pending' means it still needs to be shipped
        if ($statusStr === 'paid' || $statusStr === 'pending') {
            $stats['pending_orders'] += $st['count'];
        } else {
            $stats['shipped_orders'] += $st['count'];
        }
    }

    // 4. Get 3 Most Recent Orders for the List
    $stmt = $pdo->prepare("
        SELECT o.created_at, o.id as order_id, p.title, u.full_name as customer_name, o.status 
        FROM order_items oi 
        JOIN orders o ON oi.order_id = o.id 
        JOIN products p ON oi.product_id = p.id 
        JOIN users u ON o.customer_id = u.id 
        WHERE oi.vendor_id = ? 
        GROUP BY o.id 
        ORDER BY o.created_at DESC 
        LIMIT 3
    ");
    $stmt->execute([$vendor_id]);
    $stats['recent_orders'] = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode($stats);
    exit;
}
// ---------- ADMIN PANEL ----------
elseif ($action === 'get_admin_dashboard') {
    $stats = [
        'total_users' => $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn(),
        'total_stores' => $pdo->query("SELECT COUNT(*) FROM users WHERE role='vendor'")->fetchColumn(),
        'total_products' => $pdo->query("SELECT COUNT(*) FROM products")->fetchColumn(),
        'total_orders' => $pdo->query("SELECT COUNT(*) FROM orders")->fetchColumn(),
        'chart_data' => [],
        'pie_data' => []
    ];
    
    // Get orders by day for the Line chart
    $chart = $pdo->query("SELECT DATE(created_at) as date, COUNT(*) as count FROM orders GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 7")->fetchAll(PDO::FETCH_ASSOC);
    $stats['chart_data'] = array_reverse($chart); 
    
    // Get user roles distribution for the Pie chart
    $stats['pie_data'] = $pdo->query("SELECT role, COUNT(*) as count FROM users GROUP BY role")->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode($stats);
    exit;
}
elseif ($action === 'get_all_users_admin') {
    $stmt = $pdo->query("SELECT id, full_name, email, role, account_status, password_hash FROM users ORDER BY id DESC");
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}
elseif ($action === 'get_all_stores_admin') {
    $stmt = $pdo->query("SELECT id, shop_name, shop_description, full_name, email, account_status, store_rating FROM users WHERE role = 'vendor' ORDER BY id DESC");
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}
elseif ($action === 'get_all_products_admin') {
    // Added p.product_image to the SELECT statement
    $stmt = $pdo->query("SELECT p.id, p.title, p.price, p.stock, p.category, p.product_image, u.shop_name FROM products p JOIN users u ON p.vendor_id = u.id ORDER BY p.id DESC");
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}
elseif ($action === 'get_pending_vendors') {
    $stmt = $pdo->query("SELECT * FROM users WHERE role = 'vendor' AND account_status = 'pending'");
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}
elseif ($action === 'approve_vendor' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = $_POST['vendor_id'] ?? 0;
    $pdo->prepare("UPDATE users SET account_status = 'approved' WHERE id = ?")->execute([$id]);
    echo json_encode(["success"=>true, "message"=>"Vendor approved!"]);
    exit;
}
elseif ($action === 'reject_vendor' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = $_POST['vendor_id'] ?? 0;
    $pdo->prepare("DELETE FROM users WHERE id = ?")->execute([$id]);
    echo json_encode(["success"=>true, "message"=>"Vendor rejected and deleted!"]);
    exit;
}
?>