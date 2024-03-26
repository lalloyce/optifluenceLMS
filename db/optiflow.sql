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
    nationalId INT(8) NOT NULL UNIQUE,
    occupation VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    county VARCHAR(255) NOT NULL,
    mobileNumber VARCHAR(10) NOT NULL,
    email VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    age int default 0
    );

CREATE TABLE loans (
    loan_num INT AUTO_INCREMENT PRIMARY KEY,
    loan_amount INT NOT NULL,
    interest_rate INT NOT NULL,
    loan_period INT NOT NULL,
    borrower_id INT,
    loan_type VARCHAR(255) NOT NULL,
    loan_status VARCHAR(255) NOT NULL DEFAULT 'Active',
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    closure_date DATE DEFAULT NULL,
    penalty_amount DECIMAL(10,2) DEFAULT 0.00,
    loan_balance INT NOT NULL,
    FOREIGN KEY (borrower_id) REFERENCES borrowers(nationalId)
);

CREATE TABLE repayments (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_num INT NOT NULL,
    repayment_amount INT NOT NULL,
    repayment_date DATE NOT NULL,
    repayment_status VARCHAR(255) NOT NULL,
    borrower_id INT,
    FOREIGN KEY (loan_num) REFERENCES loans(loan_num),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(nationalId)
);

DELIMITER //
    CREATE EVENT levy_penalty
    ON SCHEDULE EVERY 1 DAY
    STARTS CONCAT(CURDATE() + INTERVAL 1 DAY, ' 00:01:00')
    DO
      BEGIN
        UPDATE loans
        SET penalty_amount = loan_balance * 0.1,
            loan_balance = loan_balance + penalty_amount,
            loan_status = 'Default'
        WHERE DATEDIFF(CURRENT_DATE, loan_date) > 30
        AND loan_balance > 0;
      END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER calculate_age_before_insert
BEFORE INSERT ON borrowers
FOR EACH ROW
BEGIN
    SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.dob, CURDATE());
END;//
DELIMITER ;

DELIMITER //
CREATE EVENT update_ages
ON SCHEDULE EVERY 1 YEAR
STARTS CURDATE() + INTERVAL 1 DAY
DO
BEGIN
    UPDATE borrowers SET age = TIMESTAMPDIFF(YEAR, dob, CURDATE());
END;//
DELIMITER ;