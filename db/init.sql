DROP DATABASE IF EXISTS cloud;
CREATE DATABASE cloud;
USE cloud;

-- Create users table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create posts table
CREATE TABLE post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    likes INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
);

-- Create post_likes table
CREATE TABLE post_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    like_type ENUM('like', 'dislike') NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY (post_id, user_id)
);

-- Insert default categories
INSERT INTO category (name) VALUES ('General');
INSERT INTO category (name) VALUES ('Science');
INSERT INTO category (name) VALUES ('Technology');
INSERT INTO category (name) VALUES ('Entertainment');
INSERT INTO category (name) VALUES ('Sports');
