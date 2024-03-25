DROP DATABASE IF EXISTS optiflow;
CREATE DATABASE optiflow;
USE optiflow;

SET time_zone = '+03:00';
SET NAMES 'utf8mb4';

CREATE TABLE optiflow.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_attempts INT DEFAULT 0,
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_requested_at datetime DEFAULT NULL
);

INSERT INTO users (username, password, email) VALUES ('admin', '$2y$10$PF6lpgZN3kEGxlfmW9mq7.deevdXw.JXCJeZToEhZ/fwTVBsuud6m', 'lalloyce@gmail.com');