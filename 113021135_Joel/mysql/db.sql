-- =============================================
-- BookHaven Database Setup
-- =============================================

CREATE DATABASE IF NOT EXISTS bookstore;
USE bookstore;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_wishlist (user_id, book_id)
);

CREATE TABLE IF NOT EXISTS site_visits (
    id INT PRIMARY KEY DEFAULT 1,
    count INT DEFAULT 0
);

INSERT INTO site_visits (count) VALUES (0)
ON DUPLICATE KEY UPDATE count = count;

INSERT INTO books (title, author, description) VALUES
('The Midnight Library', 'Matt Haig', 'A story between life and death, full of hope and regrets.'),
('Dune', 'Frank Herbert', 'A science fiction masterpiece about politics, religion, and ecology.'),
('The Alchemist', 'Paulo Coelho', 'A journey of self-discovery and following your dreams.'),
('Atomic Habits', 'James Clear', 'Practical guide to building good habits and breaking bad ones.'),
('The Silent Patient', 'Alex Michaelides', 'A psychological thriller that will keep you guessing.'),
('Educated', 'Tara Westover', 'A memoir about a woman who leaves her survivalist family for education.'),
('Project Hail Mary', 'Andy Weir', 'An incredible sci-fi adventure about saving humanity.'),
('The Housemaid', 'Freida McFadden', 'A gripping psychological thriller full of twists.');
