-- Schema for Optifluence LMS Loan Management System

CREATE TABLE loan_product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    interest_rate DECIMAL(5, 2) NOT NULL,
    minimum_amount DECIMAL(10, 2) NOT NULL,
    maximum_amount DECIMAL(10, 2) NOT NULL,
    minimum_term INT NOT NULL,
    maximum_term INT NOT NULL,
    processing_fee DECIMAL(5, 2) NOT NULL,
    term_months INT NOT NULL,
    grace_period_months INT NOT NULL,
    penalty_rate DECIMAL(5, 2) DEFAULT 10.00,
    insurance_fee DECIMAL(5, 2) DEFAULT 0.00,
    required_documents JSON,
    eligibility_criteria JSON,
    high_risk_max_amount DECIMAL(10, 2) NOT NULL,
    medium_risk_max_amount DECIMAL(10, 2) NOT NULL,
    moderate_risk_max_amount DECIMAL(10, 2) NOT NULL,
    auto_reject_below DECIMAL(5, 2) DEFAULT 30,
    auto_approve_above DECIMAL(5, 2) DEFAULT 80,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE loan_application (
    id SERIAL PRIMARY KEY,
    application_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT REFERENCES customers(id) ON DELETE PROTECT,
    loan_product_id INT REFERENCES loan_product(id) ON DELETE PROTECT,
    amount_requested DECIMAL(10, 2) NOT NULL,
    term_months INT NOT NULL,
    purpose TEXT,
    employment_status VARCHAR(20),
    monthly_income DECIMAL(10, 2),
    other_loans TEXT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE loan_guarantor (
    id SERIAL PRIMARY KEY,
    loan_id INT REFERENCES loan(id) ON DELETE CASCADE,
    guarantor_id INT REFERENCES customers(id) ON DELETE PROTECT,
    guarantee_amount DECIMAL(10, 2) NOT NULL,
    guarantee_percentage DECIMAL(5, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    id_document VARCHAR(255),
    income_proof VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (loan_id, guarantor_id)
);

CREATE TABLE repayment_schedule (
    id SERIAL PRIMARY KEY,
    loan_id INT REFERENCES loan(id) ON DELETE CASCADE,
    installment_number INT NOT NULL,
    due_date DATE NOT NULL,
    principal_amount DECIMAL(10, 2) NOT NULL,
    interest_amount DECIMAL(10, 2) NOT NULL,
    penalty_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    paid_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'PENDING',
    paid_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (loan_id, installment_number)
);

CREATE TABLE risk_alert (
    id SERIAL PRIMARY KEY,
    loan_application_id INT REFERENCES loan_application(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

CREATE TABLE transaction (
    id SERIAL PRIMARY KEY,
    loan_id INT REFERENCES loan(id) ON DELETE CASCADE,
    repayment_schedule_id INT REFERENCES repayment_schedule(id) ON DELETE SET NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    payment_method VARCHAR(50),
    payment_details JSON,
    notes TEXT,
    processed_by INT REFERENCES accounts(id) ON DELETE SET NULL,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
