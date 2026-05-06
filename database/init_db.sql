-- ============================================================
-- Enterprise SQL Analyst Agent - Database Initialization
-- Run this in your Neon Console SQL Editor to get started.
-- ============================================================

-- 1. Create Tables
CREATE TABLE IF NOT EXISTS customers (
    customer_id   SERIAL PRIMARY KEY,
    company_name  VARCHAR(255) NOT NULL,
    industry      VARCHAR(100),
    region        VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS products (
    product_id    SERIAL PRIMARY KEY,
    product_name  VARCHAR(255) NOT NULL,
    category      VARCHAR(100),
    price         DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id       SERIAL PRIMARY KEY,
    customer_id   INTEGER REFERENCES customers(customer_id),
    product_id    INTEGER REFERENCES products(product_id),
    sale_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity      INTEGER NOT NULL
);

-- 2. Seed Sample Data
INSERT INTO customers (company_name, industry, region) VALUES
('Tech Corp',          'Technology',  'North America'),
('Global Logistics',   'Logistics',   'Europe'),
('Retail Giant',       'Retail',      'Asia'),
('Health Plus',        'Healthcare',  'North America'),
('Energy Solutions',   'Energy',      'Europe'),
('Finance Hub',        'Finance',     'Asia'),
('Smart Manufacturing','Manufacturing','North America');

INSERT INTO products (product_name, category, price) VALUES
('Cloud Server',    'Computing',   1200.00),
('Smart Watch',     'Electronics',  199.99),
('Industrial Drill','Machinery',    450.50),
('Diagnostic Kit',  'Medical',       85.00),
('Solar Panel',     'Energy',       320.00),
('Laptop Pro',      'Computing',   1599.00),
('Wireless Sensor', 'Electronics',   75.00);

INSERT INTO sales (customer_id, product_id, quantity, sale_date) VALUES
(1, 1, 5,  '2024-01-10 10:00:00'),
(2, 3, 2,  '2024-01-12 14:30:00'),
(3, 2, 10, '2024-01-15 09:15:00'),
(4, 4, 20, '2024-01-18 11:45:00'),
(5, 5, 8,  '2024-01-20 16:20:00'),
(1, 2, 3,  '2024-01-22 13:10:00'),
(3, 1, 1,  '2024-01-25 08:50:00'),
(6, 6, 4,  '2024-02-01 10:30:00'),
(7, 7, 15, '2024-02-05 12:00:00'),
(2, 5, 6,  '2024-02-10 15:45:00'),
(5, 1, 2,  '2024-02-14 09:00:00'),
(1, 6, 3,  '2024-02-18 11:30:00'),
(4, 7, 25, '2024-02-20 14:00:00'),
(3, 3, 4,  '2024-02-25 10:15:00');
