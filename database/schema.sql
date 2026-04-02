-- Farm Connect Platform MySQL Schema (Django will generate most via migrations)
-- Run after Django migrations

CREATE DATABASE IF NOT EXISTS farmconnect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE farmconnect;

-- Manual indexes or additional constraints can go here
-- Django models handle tables

-- Example seed data (run after migrate)
-- INSERT INTO market_prices (crop_name, price, updated_at) VALUES ('Rice', 25.50, NOW());
-- INSERT INTO market_prices (crop_name, price, updated_at) VALUES ('Maize', 18.75, NOW());

