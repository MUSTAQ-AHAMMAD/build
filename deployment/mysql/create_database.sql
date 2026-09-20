-- ==============================================================================
-- BUILD+ ENTERPRISE PORTAL — PRODUCTION DATABASE CREATION SCRIPT
-- Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci | Engine: InnoDB
-- ==============================================================================
-- INSTRUCTIONS:
-- 1. Replace DATABASE_NAME with your production database name (e.g. cpaneluser_buildplus)
-- 2. Replace DATABASE_USER with your database user (e.g. cpaneluser_dbuser)
-- 3. Replace DATABASE_PASSWORD with your strong random production password
-- ==============================================================================

-- 1. Create Database with full Unicode support (multilingual, emoji-safe, special characters)
CREATE DATABASE IF NOT EXISTS `DATABASE_NAME`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Create User (Skip if created via cPanel MySQL Database Wizard)
CREATE USER IF NOT EXISTS 'DATABASE_USER'@'localhost'
    IDENTIFIED BY 'DATABASE_PASSWORD';

-- 3. Grant Privileges
GRANT ALL PRIVILEGES ON `DATABASE_NAME`.* TO 'DATABASE_USER'@'localhost';

-- 4. Apply Changes
FLUSH PRIVILEGES;

-- ==============================================================================
-- DATABASE CONFIGURATION SUMMARY:
-- Database Name: DATABASE_NAME
-- Database User: DATABASE_USER
-- Database Host: localhost (or 127.0.0.1)
-- Database Port: 3306
-- Database Charset: utf8mb4
-- Database Collation: utf8mb4_unicode_ci
-- ==============================================================================
