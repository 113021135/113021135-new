-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 30, 2026 at 04:53 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `secondhand_market`
--

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `favorites`
--

CREATE TABLE `favorites` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `from_user_id` int(11) NOT NULL,
  `to_user_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `timestamp` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `from_user_id`, `to_user_id`, `product_id`, `message`, `is_read`, `timestamp`) VALUES
(1, 4, 3, NULL, 'test', 1, '2026-05-28 21:12:04'),
(2, 3, 4, NULL, 'yes', 1, '2026-05-28 21:12:37'),
(3, 4, 3, NULL, 'hello', 1, '2026-05-28 22:47:46'),
(4, 3, 4, NULL, 'test', 1, '2026-05-28 22:48:19');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(50) DEFAULT 'cash',
  `status` varchar(50) DEFAULT 'paid',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `customer_id`, `total_amount`, `payment_method`, `status`, `created_at`) VALUES
(1, 4, 12000.00, 'cash', 'paid', '2026-05-28 05:54:12'),
(2, 4, 11400.00, 'cash', 'Delivered', '2026-05-30 12:59:33'),
(3, 4, 550.00, 'digital_wallet', 'Pending', '2026-05-30 13:37:05');

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `vendor_id` int(11) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `price_at_purchase` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`id`, `order_id`, `product_id`, `vendor_id`, `quantity`, `price_at_purchase`) VALUES
(1, 1, 11, 3, 1, 12000.00),
(2, 2, 16, 14, 1, 9900.00),
(3, 2, 15, 8, 1, 1500.00),
(4, 3, 28, 14, 1, 300.00),
(5, 3, 27, 14, 1, 100.00),
(6, 3, 25, 14, 1, 150.00);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `vendor_id` int(11) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `sale_price` decimal(10,2) DEFAULT NULL,
  `discount_type` enum('none','permanent','temporary') DEFAULT 'none',
  `discount_expires_at` datetime DEFAULT NULL,
  `category` varchar(50) NOT NULL,
  `stock` int(11) DEFAULT 1,
  `product_image` text DEFAULT NULL,
  `sales_count` int(11) DEFAULT 0,
  `average_rating` decimal(2,1) DEFAULT 0.0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `vendor_id`, `title`, `description`, `price`, `sale_price`, `discount_type`, `discount_expires_at`, `category`, `stock`, `product_image`, `sales_count`, `average_rating`) VALUES
(5, 3, 'Nike Lebron 22', 'a little bit worn... ', 3500.00, NULL, 'none', NULL, 'shoes', 3, '0f0b2085108afc5eb1cfa7182476bd56.webp', 0, 0.0),
(9, 3, 'Lebron 20', 'BNIB', 6000.00, NULL, 'none', NULL, 'shoes,women', 1, 'd7d71abbd04528c1894924bfc570f15b.jpg', 0, 0.0),
(10, 8, 'Luka Doncic Shirt', 'just worn it once and i think its too big for me...', 1500.00, NULL, 'none', NULL, 'clothes,women', 1, 'cd22623b29b96d421e834399d3e8118d.jpg', 0, 0.0),
(11, 3, 'Lining Gamma 2', '100% BNIB (Wrong Size)', 12000.00, NULL, 'none', NULL, 'shoes,man', 1, '4f18a2e7043c2541fae827ad8f0b50d5.webp', 0, 0.0),
(12, 13, 'VERY GOOD CONDITION COOKING PAN', '90% New', 497.00, NULL, 'none', NULL, 'household', 1, '2e58cf5241807051cd3dd38d70561175.webp', 0, 0.0),
(13, 13, 'CAMPING GAS STOVE', 'Very Good Deal, if you buy this stove, lets camp together with me hehehe', 500.00, NULL, 'none', NULL, 'household', 1, '847b6dbd429566198aa9dbf209fbc3c0.jpg', 0, 0.0),
(14, 3, 'GT Cut 4', 'BNIB', 6600.00, NULL, 'none', NULL, 'shoes,man', 1, '151b181f207b4689ab4c6368623a50f9.jpg', 0, 0.0),
(15, 8, 'Stephen Curry Shirt', '100% New', 1500.00, NULL, 'none', NULL, 'clothes,man', 0, '73bf0251e0873adf40fe21f6ff0fffbf.jpg', 0, 0.0),
(16, 14, 'Luxury Designer Bags', '100% New', 12000.00, 9900.00, 'permanent', NULL, 'bags,women', 0, 'bf73e71b052e3538a7f3c0178c849d04.jpg', 0, 0.0),
(17, 14, 'Gucci Bag', 'VERY GOOD DEALS PLEASE BUY I NEED MONEY TO GO CLUBBING', 9000.00, 5000.00, 'temporary', '2026-05-31 01:43:46', 'bags,women', 1, '2d1821a33ca78eda584a7e8db8388d12.webp', 0, 0.0),
(18, 3, 'kobe 6', 'good', 10000.00, NULL, 'none', NULL, 'shoes,man', 1, 'd81e3536f07070d30cbf83078dd25b34.jpg', 0, 0.0),
(19, 3, 'Airpods 4 Anc', 'One time use only', 3000.00, 200.00, 'permanent', NULL, 'electronics,man,women', 3, 'dd41be974a9aa57b0e92c4e6cb617c7b.jpg', 0, 0.0),
(20, 3, 'Iphone 17 Pro Max', 'Like new', 30000.00, NULL, 'none', NULL, 'electronics,man,women', 1, '9c27fc1898f97bcc28c7d72325b63e77.jpg', 0, 0.0),
(21, 5, 'Nintendo Switch', '2025 product', 9000.00, NULL, 'none', NULL, 'electronics,games,child', 2, '61eca01513d602cb5ef853e300f71e60.jpg', 0, 0.0),
(22, 5, 'Ps5', 'used 2 years', 8000.00, 7000.00, 'permanent', NULL, 'electronics,games,man', 1, 'dde4584969550e6b34d78e3736326f6e.webp', 0, 0.0),
(23, 5, 'Starwars Lego', 'Brand new', 700.00, NULL, 'none', NULL, 'games,child', 1, 'bbb4c5ebe0580dbcf5ed28fffcdbdc61.jpg', 0, 0.0),
(24, 5, 'Futsal Decker', 'new', 300.00, NULL, 'none', NULL, 'sports', 1, '79949140adeac68553192674208d31ff.png', 0, 0.0),
(25, 14, 'Rich Dad Poor Dad', 'like new', 150.00, NULL, 'none', NULL, 'books', 0, '7187b6a4d300ee8d9c541920cd7d32ab.jpg', 0, 0.0),
(26, 14, 'Lego Ninjago', 'Brand new', 400.00, 380.00, 'permanent', NULL, 'games,child', 1, '5a840c28790975db0b5bc712e667a5e7.jpg', 0, 0.0),
(27, 14, 'Psychology of money', '1 year', 100.00, NULL, 'none', NULL, 'books', 0, '5558d865c9ce00f946ccb80c61c6955c.jpg', 0, 0.0),
(28, 14, 'Wilson Ball ', 'new', 300.00, NULL, 'none', NULL, 'sports', 0, '2f16252d222057ce1426105c54f57262.jpg', 0, 0.0),
(29, 14, 'IKEA Cupboard', 'Good condition', 500.00, NULL, 'none', NULL, 'household', 1, '4ddbfc472e081f837cae067d3f4c775f.webp', 0, 0.0);

-- --------------------------------------------------------

--
-- Table structure for table `product_images`
--

CREATE TABLE `product_images` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `image_filename` varchar(255) NOT NULL,
  `sort_order` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_images`
--

INSERT INTO `product_images` (`id`, `product_id`, `image_filename`, `sort_order`) VALUES
(18, 11, '4f18a2e7043c2541fae827ad8f0b50d5.webp', 0),
(19, 11, '8c9130a53d56e4713c3f8623d5ce2a43.webp', 1),
(20, 11, 'b65793c907ebea583f6b4ea911113bf7.jpg', 2),
(25, 9, 'd7d71abbd04528c1894924bfc570f15b.jpg', 0),
(26, 9, 'a678c7a087014eeaa27e5444a1fc1f63.jpg', 1),
(27, 12, '2e58cf5241807051cd3dd38d70561175.webp', 0),
(28, 13, '847b6dbd429566198aa9dbf209fbc3c0.jpg', 0),
(29, 14, '151b181f207b4689ab4c6368623a50f9.jpg', 0),
(30, 10, 'cd22623b29b96d421e834399d3e8118d.jpg', 0),
(31, 15, '73bf0251e0873adf40fe21f6ff0fffbf.jpg', 0),
(32, 16, 'bf73e71b052e3538a7f3c0178c849d04.jpg', 0),
(33, 17, '2d1821a33ca78eda584a7e8db8388d12.webp', 0),
(34, 5, '0f0b2085108afc5eb1cfa7182476bd56.webp', 0),
(35, 18, 'd81e3536f07070d30cbf83078dd25b34.jpg', 0),
(36, 19, 'dd41be974a9aa57b0e92c4e6cb617c7b.jpg', 0),
(37, 20, '9c27fc1898f97bcc28c7d72325b63e77.jpg', 0),
(38, 21, '61eca01513d602cb5ef853e300f71e60.jpg', 0),
(39, 22, 'dde4584969550e6b34d78e3736326f6e.webp', 0),
(40, 23, 'bbb4c5ebe0580dbcf5ed28fffcdbdc61.jpg', 0),
(41, 24, '79949140adeac68553192674208d31ff.png', 0),
(42, 25, '7187b6a4d300ee8d9c541920cd7d32ab.jpg', 0),
(43, 26, '5a840c28790975db0b5bc712e667a5e7.jpg', 0),
(44, 27, '5558d865c9ce00f946ccb80c61c6955c.jpg', 0),
(45, 28, '2f16252d222057ce1426105c54f57262.jpg', 0),
(46, 29, '4ddbfc472e081f837cae067d3f4c775f.webp', 0);

-- --------------------------------------------------------

--
-- Table structure for table `product_reviews`
--

CREATE TABLE `product_reviews` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL CHECK (`rating` >= 1 and `rating` <= 5),
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product_reviews`
--

INSERT INTO `product_reviews` (`id`, `product_id`, `user_id`, `rating`, `comment`, `created_at`) VALUES
(1, 11, 4, 5, 'i like this product', '2026-05-28 05:56:03'),
(2, 16, 4, 3, 'not bad', '2026-05-30 12:59:46'),
(3, 15, 4, 5, 'good', '2026-05-30 13:00:20'),
(4, 28, 4, 4, '', '2026-05-30 13:37:11'),
(5, 27, 4, 3, '', '2026-05-30 13:37:12'),
(6, 25, 4, 4, '', '2026-05-30 13:37:14');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('customer','vendor','admin') DEFAULT 'customer',
  `account_status` enum('pending','approved') DEFAULT 'approved',
  `shop_name` varchar(100) DEFAULT NULL,
  `shop_description` text DEFAULT NULL,
  `shop_profile_pic` varchar(255) DEFAULT 'default_shop.png',
  `store_rating` decimal(2,1) DEFAULT 0.0,
  `store_name` varchar(100) DEFAULT NULL,
  `profile_picture` varchar(255) DEFAULT 'default-avatar.png',
  `last_active` timestamp NOT NULL DEFAULT current_timestamp(),
  `rating` decimal(2,1) DEFAULT 0.0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `role`, `account_status`, `shop_name`, `shop_description`, `shop_profile_pic`, `store_rating`, `store_name`, `profile_picture`, `last_active`, `rating`) VALUES
(1, 'Alex Vando', 'vando@store.com', '$2y$10$abcdefghijklmnopqrstuv', 'vendor', 'approved', 'Vando Luxury Thrift', NULL, 'default_shop.png', 4.9, NULL, 'default-avatar.png', '2026-05-19 03:31:01', 0.0),
(3, 'vando', 'vandowangs@gmail.com', '$2y$10$7vCnN5Pbo.f5dxDNG9PlpO236RqMl2aNDHqiF5BcsG0S61njAiuDe', 'vendor', 'approved', 'vandeo store', 'murah su', '6f4ecb49cddde746123c0e7c00adb176.jpg', 5.0, NULL, 'default-avatar.png', '2026-05-30 13:23:56', 0.0),
(4, 'joel', 'joel@gmail.com', '$2y$10$6NoPTS7dQLZ4V0nbXyA/s.jVrzTV9.48zpGEc2p.5NpR9cViUV/kO', 'customer', 'approved', NULL, NULL, 'default_shop.png', 0.0, NULL, 'default-avatar.png', '2026-05-30 13:37:23', 0.0),
(5, 'kenlynw', 'kenly@gmail.com', '$2y$10$B3NBsX5TJKlwjaMuvdiIneYHjrD.ErB9G.jRmfRKT6VyXKb18UiO2', 'vendor', 'approved', 'Kenly Store', 'very good quality store...', '9eba6ad753a4f36c66c56b389afd3261.jpg', 0.0, NULL, 'default-avatar.png', '2026-05-30 13:28:19', 0.0),
(8, 'kenlynw', 'kenlyn@gmail.com', '$2y$10$DmsbLysZ.U9CKyUYvnXCeOJlRzG4YFXN9VUXgL06nQ1B7Cwn.du5q', 'vendor', 'approved', 'Kenly Store', 'p', '9eba6ad753a4f36c66c56b389afd3261.jpg', 0.0, NULL, 'default-avatar.png', '2026-05-30 11:44:27', 0.0),
(11, 'Administrator', 'admin@secondmarket.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin', 'approved', NULL, NULL, 'default_shop.png', 0.0, NULL, 'default-avatar.png', '2026-05-19 04:48:39', 0.0),
(13, 'Alvin', 'alvin@gmail.com', '$2y$10$S4qhxCnJA.39n2WrpycAdu06VNPsQ6Nc6TdTAmpLWekc6LJsyTEVy', 'vendor', 'approved', 'Alvin Store', 'CHEAP AF', '1b58c19d5c4e5f02c10fbb3d1a79033e.jpeg', 0.0, NULL, 'default-avatar.png', '2026-05-19 08:41:26', 0.0),
(14, 'BIGBOSS STARGIRL', 'kay@gmail.com', '$2y$10$z0kqpY/UvqEwRO.LUMJIGeDDBeVzWy4CKuXWZQhrEabIiW26BKLfG', 'vendor', 'approved', 'STARGIRL STORE', 'izinnn', 'images (4).jpg', 4.0, NULL, 'default-avatar.png', '2026-05-30 14:53:05', 0.0),
(15, 'ken', 'ken@gmail.com', '$2y$10$9pRDOmsrEKUvxlt1mTRPW.rD7sZKp3BfwFiCgubszLYZ6lqsLM/6a', 'customer', 'approved', NULL, NULL, 'default_shop.png', 0.0, NULL, 'default-avatar.png', '2026-05-30 12:10:21', 0.0),
(17, 'kenet', 'kenet@gmail.com', '$2y$10$MWScM6drPOe9R7aQdLyWQOvqcXI07JVKmn4qp7F8oM863N5itZWxW', 'vendor', 'pending', 'kenet', 'hello', 'default_shop.png', 0.0, NULL, 'default-avatar.png', '2026-05-30 12:12:12', 0.0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `favorites`
--
ALTER TABLE `favorites`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_favorite` (`user_id`,`product_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `from_user_id` (`from_user_id`),
  ADD KEY `to_user_id` (`to_user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `vendor_id` (`vendor_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `vendor_id` (`vendor_id`);

--
-- Indexes for table `product_images`
--
ALTER TABLE `product_images`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `product_reviews`
--
ALTER TABLE `product_reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;

--
-- AUTO_INCREMENT for table `favorites`
--
ALTER TABLE `favorites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `product_images`
--
ALTER TABLE `product_images`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT for table `product_reviews`
--
ALTER TABLE `product_reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`from_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`to_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_3` FOREIGN KEY (`vendor_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_images`
--
ALTER TABLE `product_images`
  ADD CONSTRAINT `product_images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_reviews`
--
ALTER TABLE `product_reviews`
  ADD CONSTRAINT `product_reviews_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `product_reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
