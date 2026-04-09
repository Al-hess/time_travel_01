-- This script removes all tables related to the Cooking App (Kelia App)
-- from the database, while preserving the Time Travel project tables.

-- We use CASCADE to automatically drop dependent objects (like foreign key constraints)

DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS steps CASCADE;
DROP TABLE IF EXISTS recipes CASCADE;
DROP TABLE IF EXISTS movies CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS counters CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- Note: Time Travel tables ("Customer", "Booking", "Timeline", "Packages", 
-- "MinuteMen", "Languages", "Identities", "Payments") will be left completely intact.
