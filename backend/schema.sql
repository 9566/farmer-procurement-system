-- ============================================================
-- SMART FARMER PROCUREMENT SYSTEM
-- DATABASE SCHEMA
-- ============================================================

CREATE DATABASE IF NOT EXISTS farmer_procurement
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE farmer_procurement;


-- ============================================================
-- FARMERS
-- ============================================================

CREATE TABLE IF NOT EXISTS farmers (

    farmer_id INT PRIMARY KEY AUTO_INCREMENT,

    name VARCHAR(100) NOT NULL,

    mobile VARCHAR(15) UNIQUE NOT NULL,

    email VARCHAR(100),

    password VARCHAR(255) NOT NULL,

    address TEXT,

    village VARCHAR(100),

    district VARCHAR(100),

    state VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- PROCUREMENT CENTRES
-- ============================================================

CREATE TABLE IF NOT EXISTS procurement_centres (

    centre_id INT PRIMARY KEY AUTO_INCREMENT,

    centre_name VARCHAR(150) NOT NULL,

    location VARCHAR(255),

    district VARCHAR(100),

    capacity_per_day INT,

    opening_time TIME,

    closing_time TIME
);


-- ============================================================
-- CROPS
-- ============================================================

CREATE TABLE IF NOT EXISTS crops (

    crop_id INT PRIMARY KEY AUTO_INCREMENT,

    crop_name VARCHAR(100) NOT NULL,

    minimum_support_price DECIMAL(10,2),

    unit VARCHAR(20)
);


-- ============================================================
-- BOOKINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS bookings (

    booking_id INT PRIMARY KEY AUTO_INCREMENT,

    farmer_id INT NOT NULL,

    centre_id INT NOT NULL,

    crop_id INT NOT NULL,

    quantity DECIMAL(10,2) NOT NULL,

    booking_date DATE NOT NULL,

    slot VARCHAR(50) NOT NULL,

    token_number INT NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'BOOKED',

    UNIQUE KEY uq_booking_centre_date_token
    (
        centre_id,
        booking_date,
        token_number
    ),

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(farmer_id),

    FOREIGN KEY (centre_id)
        REFERENCES procurement_centres(centre_id),

    FOREIGN KEY (crop_id)
        REFERENCES crops(crop_id)
);


-- ============================================================
-- QUEUE
-- ============================================================

CREATE TABLE IF NOT EXISTS queue (

    queue_id INT PRIMARY KEY AUTO_INCREMENT,

    booking_id INT NOT NULL UNIQUE,

    centre_id INT NOT NULL,

    token_number INT NOT NULL,

    queue_position INT NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'WAITING',

    UNIQUE KEY uq_queue_centre_booking
    (
        centre_id,
        booking_id
    ),

    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id),

    FOREIGN KEY (centre_id)
        REFERENCES procurement_centres(centre_id)
);


-- ============================================================
-- PROCUREMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS procurement (

    procurement_id INT PRIMARY KEY AUTO_INCREMENT,

    booking_id INT NOT NULL UNIQUE,

    actual_quantity DECIMAL(10,2),

    quality_status VARCHAR(50),

    procurement_date DATE,

    procurement_status VARCHAR(30)
        NOT NULL DEFAULT 'PENDING',

    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id)
);


-- ============================================================
-- PAYMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS payments (

    payment_id INT PRIMARY KEY AUTO_INCREMENT,

    booking_id INT NOT NULL UNIQUE,

    farmer_id INT NOT NULL,

    amount DECIMAL(10,2) NOT NULL DEFAULT 0,

    payment_method VARCHAR(50),

    transaction_id VARCHAR(100),

    payment_status VARCHAR(30)
        NOT NULL DEFAULT 'PENDING',

    payment_date TIMESTAMP NULL,

    FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id),

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(farmer_id)
);


-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS notifications (

    notification_id INT PRIMARY KEY AUTO_INCREMENT,

    farmer_id INT NOT NULL,

    message TEXT NOT NULL,

    notification_type VARCHAR(50),

    is_read BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (farmer_id)
        REFERENCES farmers(farmer_id)
);


-- ============================================================
-- STAFF USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS staff_users (

    staff_id INT PRIMARY KEY AUTO_INCREMENT,

    name VARCHAR(100) NOT NULL,

    mobile VARCHAR(15) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    role VARCHAR(20) NOT NULL,

    centre_id INT NULL,

    FOREIGN KEY (centre_id)
        REFERENCES procurement_centres(centre_id)
);


-- ============================================================
-- SAMPLE PROCUREMENT CENTRE
-- ============================================================

INSERT INTO procurement_centres
(
    centre_name,
    location,
    district,
    capacity_per_day,
    opening_time,
    closing_time
)

SELECT
    'Lucknow Mandi Centre',
    'Sector 5, Lucknow',
    'Lucknow',
    100,
    '08:00:00',
    '18:00:00'

WHERE NOT EXISTS
(
    SELECT 1
    FROM procurement_centres
    WHERE centre_name = 'Lucknow Mandi Centre'
);


-- ============================================================
-- SAMPLE CROPS
-- ============================================================

INSERT INTO crops
(
    crop_name,
    minimum_support_price,
    unit
)

SELECT
    'Wheat',
    2275.00,
    'quintal'

WHERE NOT EXISTS
(
    SELECT 1
    FROM crops
    WHERE crop_name = 'Wheat'
);


INSERT INTO crops
(
    crop_name,
    minimum_support_price,
    unit
)

SELECT
    'Rice',
    2183.00,
    'quintal'

WHERE NOT EXISTS
(
    SELECT 1
    FROM crops
    WHERE crop_name = 'Rice'
);


INSERT INTO crops
(
    crop_name,
    minimum_support_price,
    unit
)

SELECT
    'Sugarcane',
    340.00,
    'quintal'

WHERE NOT EXISTS
(
    SELECT 1
    FROM crops
    WHERE crop_name = 'Sugarcane'
);