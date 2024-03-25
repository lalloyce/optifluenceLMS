DROP DATABASE IF EXISTS optiflow;
CREATE DATABASE optiflow;
USE optiflow;

SET time_zone = '+03:00';
SET NAMES 'utf8mb4';

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_attempts INT DEFAULT 0,
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_requested_at datetime DEFAULT NULL,
    last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, email) VALUES ('admin', 'D#FR$GG#D', 'lalloyce@gmail.com');

CREATE TABLE borrowers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    nationalId INT(8) NOT NULL,
    location VARCHAR(255) NOT NULL,
    occupation VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    county VARCHAR(255) NOT NULL,
    mobileNumber VARCHAR(10) NOT NULL,
    email VARCHAR(255) NOT NULL,
    dob DATE NOT NULL
    );

CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_amount INT NOT NULL,
    interest_rate INT NOT NULL,
    loan_period INT NOT NULL,
    borrower_id INT,
    loan_type VARCHAR(255) NOT NULL,
    loan_purpose VARCHAR(255) NOT NULL,
    loan_status VARCHAR(255) NOT NULL,
    loan_date DATE NOT NULL,
    loan_due_date DATE NOT NULL,
    loan_repayment_date DATE NOT NULL,
    loan_repayment_amount INT NOT NULL,
    loan_penalty_amount DECIMAL(10,2) DEFAULT 0.00,
    loan_balance INT NOT NULL,
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
);

CREATE TABLE repayments (
    repayment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
    repayment_amount INT NOT NULL,
    repayment_date DATE NOT NULL,
    repayment_status VARCHAR(255) NOT NULL,
    borrower_id INT,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
);