-- supabase_reset.sql
-- SUPABASE FULL DATABASE RESET SCRIPT
-- WARNING: This script deletes ALL cloud data and rebuilds the entire schema.
-- Only reference data (Packages, Languages, MinuteMen, Violations) is re-inserted.
-- Transactional data (Bookings, Payments, Customers, etc.) will NOT be restored.

-- ===========================================
-- STEP 1: DROP EXISTING TABLES
-- Dropped in reverse dependency order to avoid foreign key constraint errors.
-- CASCADE also removes any dependent constraints on other tables automatically.
-- ===========================================
DROP TABLE IF EXISTS "Trip_Violations" CASCADE;
DROP TABLE IF EXISTS "Identities" CASCADE;
DROP TABLE IF EXISTS "Payments" CASCADE;
DROP TABLE IF EXISTS "Booking" CASCADE;
DROP TABLE IF EXISTS "Violations" CASCADE;
DROP TABLE IF EXISTS "MinuteMen" CASCADE;
DROP TABLE IF EXISTS "Languages" CASCADE;
DROP TABLE IF EXISTS "Timeline" CASCADE;
DROP TABLE IF EXISTS "Packages" CASCADE;
DROP TABLE IF EXISTS "Customer" CASCADE;

-- ===========================================
-- STEP 2: RECREATE TABLES
-- Created in dependency order (independent tables first, dependent last).
-- SERIAL = auto-increment integer, DOUBLE PRECISION = float, TEXT = string
-- ===========================================

-- Table: Customer
-- Stores personal traveler information
-- customer_id: SERIAL (PK), email: TEXT UNIQUE (used to prevent duplicate customers)
CREATE TABLE "Customer" (
    customer_id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    phone_num TEXT,
    address TEXT,
    birthdate TEXT,
    email TEXT UNIQUE,
    sex TEXT
);

-- Table: Packages
-- Reference table for the three available travel packages
-- package_id: SERIAL (PK), description: TEXT UNIQUE, package_rate: DOUBLE PRECISION (USD per minute)
CREATE TABLE "Packages" (
    package_id SERIAL PRIMARY KEY,
    description TEXT UNIQUE,
    package_rate DOUBLE PRECISION
);

-- Table: Timeline
-- Records the historical era visited per trip
-- timeline_id: SERIAL (PK), timeline_year: TEXT (label), map: TEXT (numeric year)
CREATE TABLE "Timeline" (
    timeline_id SERIAL PRIMARY KEY,
    timeline_year TEXT,
    map TEXT
);

-- Table: Languages
-- Reference catalog of available languages
-- language_id: SERIAL (PK), language_name: TEXT UNIQUE (prevents duplicate entries)
CREATE TABLE "Languages" (
    language_id SERIAL PRIMARY KEY,
    language_name TEXT UNIQUE
);

-- Table: MinuteMen
-- Reference table of TimeCorp agents assigned to monitor trips
-- agent_id: SERIAL (PK), badge_number: TEXT UNIQUE
CREATE TABLE "MinuteMen" (
    agent_id SERIAL PRIMARY KEY,
    badge_number TEXT UNIQUE,
    agent_name TEXT
);

-- Table: Violations
-- Reference catalog of prohibited actions with fines
-- violation_id: SERIAL (PK), crime: TEXT UNIQUE, fine_amount: DOUBLE PRECISION (USD)
CREATE TABLE "Violations" (
    violation_id SERIAL PRIMARY KEY,
    crime TEXT UNIQUE,
    penalty_description TEXT,
    fine_amount DOUBLE PRECISION
);

-- Table: Booking (Central Transaction Table)
-- Links customers, packages, timelines, and agents per trip
-- booking_id: SERIAL (PK)
-- customer_id, package_id, timeline_id, agent_id: INTEGER (foreign keys)
-- insurance, memory_reset: BOOLEAN (optional add-ons)
-- total_price: DOUBLE PRECISION (USD)
-- booking_languages: TEXT (comma-separated language IDs)
-- booking_date: TIMESTAMP (auto-filled)
CREATE TABLE "Booking" (
    booking_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES "Customer"(customer_id),
    package_id INTEGER REFERENCES "Packages"(package_id),
    timeline_id INTEGER REFERENCES "Timeline"(timeline_id),
    spawn_country TEXT,
    minutes INTEGER,
    insurance BOOLEAN,
    memory_reset BOOLEAN,
    total_price DOUBLE PRECISION,
    booking_languages TEXT,
    fame_level INTEGER,
    agent_id INTEGER REFERENCES "MinuteMen"(agent_id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Payments
-- Records the payment transaction linked to each booking
-- amount: DOUBLE PRECISION (converted currency amount), method: TEXT (e.g. "Visa")
CREATE TABLE "Payments" (
    payment_id SERIAL PRIMARY KEY,
    amount DOUBLE PRECISION,
    currency TEXT,
    method TEXT,
    customer_id INTEGER REFERENCES "Customer"(customer_id),
    booking_id INTEGER REFERENCES "Booking"(booking_id)
);

-- Table: Identities
-- Fake alias generated for non-Peasant travelers
-- booking_id: INTEGER (foreign key), fame_level: INTEGER (mirrors the booking's fame level)
CREATE TABLE "Identities" (
    identity_id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    sex TEXT,
    fame_level INTEGER,
    booking_id INTEGER REFERENCES "Booking"(booking_id)
);

-- Table: Trip_Violations (Bridge / Junction Table)
-- Many-to-many link between Booking and Violations
-- occurrence_date: TIMESTAMP (auto-filled when the violation is recorded)
CREATE TABLE "Trip_Violations" (
    trip_violation_id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES "Booking"(booking_id),
    violation_id INTEGER REFERENCES "Violations"(violation_id),
    occurrence_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- STEP 3: INSERT REFERENCE DATA ONLY
-- Only the pre-defined lookup tables are populated (no transactional data).
-- ===========================================

-- Reference data: Packages
INSERT INTO "Packages" ("package_id", "description", "package_rate") VALUES (1, 'Peasant Package', 10.0);
INSERT INTO "Packages" ("package_id", "description", "package_rate") VALUES (2, 'Quantum Query', 20.0);
INSERT INTO "Packages" ("package_id", "description", "package_rate") VALUES (3, 'Monarch Mode', 50.0);

-- Reference data: Languages (historical and modern language catalog)
INSERT INTO "Languages" ("language_id", "language_name") VALUES (1, 'Sumerian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (2, 'Akkadian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (3, 'Egyptian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (4, 'Hittite');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (5, 'Elamite');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (6, 'Sanskrit');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (7, 'Prakrit');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (8, 'Pali');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (9, 'Old Persian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (10, 'Avestan');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (11, 'Ancient Greek');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (12, 'Latin');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (13, 'Etruscan');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (14, 'Phoenician');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (15, 'Aramaic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (16, 'Hebrew');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (17, 'Ugaritic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (18, 'Coptic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (19, 'Old Church Slavonic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (20, 'Gothic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (21, 'Old English');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (22, 'Middle English');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (23, 'Modern English');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (24, 'Old Norse');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (25, 'Icelandic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (26, 'Old High German');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (27, 'Middle High German');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (28, 'Modern German');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (29, 'Yiddish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (30, 'Dutch');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (31, 'Old French');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (32, 'Middle French');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (33, 'Modern French');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (34, 'Occitan');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (35, 'Catalan');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (36, 'Italian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (37, 'Sicilian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (38, 'Spanish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (39, 'Portuguese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (40, 'Galician');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (41, 'Romanian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (42, 'Dacian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (43, 'Albanian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (44, 'Irish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (45, 'Scottish Gaelic');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (46, 'Welsh');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (47, 'Breton');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (48, 'Cornish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (49, 'Manx');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (50, 'Basque');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (51, 'Finnish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (52, 'Estonian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (53, 'Hungarian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (54, 'Maltese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (55, 'Lithuanian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (56, 'Latvian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (57, 'Prussian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (58, 'Russian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (59, 'Ukrainian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (60, 'Belarusian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (61, 'Polish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (62, 'Czech');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (63, 'Slovak');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (64, 'Serbo-Croatian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (65, 'Bulgarian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (66, 'Macedonian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (67, 'Slovene');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (68, 'Greek');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (69, 'Armenian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (70, 'Georgian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (71, 'Persian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (72, 'Kurdish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (73, 'Pashto');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (74, 'Balochi');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (75, 'Urdu');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (76, 'Hindi');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (77, 'Bengali');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (78, 'Punjabi');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (79, 'Marathi');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (80, 'Gujarati');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (81, 'Tamil');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (82, 'Telugu');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (83, 'Kannada');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (84, 'Malayalam');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (85, 'Sinhalese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (86, 'Thai');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (87, 'Lao');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (88, 'Khmer');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (89, 'Burmese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (90, 'Chinese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (91, 'Classical Chinese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (92, 'Japanese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (93, 'Korean');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (94, 'Vietnamese');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (95, 'Tibetan');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (96, 'Mongolian');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (97, 'Turkish');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (98, 'Uzbek');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (99, 'Kazakh');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (100, 'Azerbaijani');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (101, 'Turkmen');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (102, 'Tatar');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (103, 'Yakut');
INSERT INTO "Languages" ("language_id", "language_name") VALUES (104, 'Chuvash');

-- Reference data: MinuteMen (TimeCorp monitoring agents)
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (1, 'MM-001', 'Agent K');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (2, 'MM-007', 'Agent Vance');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (3, 'MM-009', 'Agent Weaver');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (4, 'MM-012', 'Agent Thorne');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (5, 'MM-042', 'Agent Sterling');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (6, 'MM-088', 'Agent Cross');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (7, 'MM-099', 'Agent Blackwood');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (8, 'MM-101', 'Agent Mercer');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (9, 'MM-314', 'Agent Pi');
INSERT INTO "MinuteMen" ("agent_id", "badge_number", "agent_name") VALUES (10, 'MM-999', 'Agent Alpha');

-- Reference data: Violations (prohibited actions, penalties, and fines)
INSERT INTO "Violations" ("violation_id", "crime", "penalty_description", "fine_amount") VALUES (1, 'Murder', 'Immediate timeline termination, final warning.', 5000.0);
INSERT INTO "Violations" ("violation_id", "crime", "penalty_description", "fine_amount") VALUES (2, 'Genocide (or attempted)', 'Immediate timeline termination, permanent ban.', 50000.0);
INSERT INTO "Violations" ("violation_id", "crime", "penalty_description", "fine_amount") VALUES (3, 'Enslavement', 'Immediate timeline termination, permanent ban.', 15000.0);
INSERT INTO "Violations" ("violation_id", "crime", "penalty_description", "fine_amount") VALUES (4, 'Rape / Sexual misconduct', 'Immediate timeline termination, permanent ban, report to authorities.', 10000.0);

-- ===========================================
-- STEP 4: SYNCHRONIZE AUTO-INCREMENT SEQUENCES
-- After manual inserts with explicit IDs, sequences must be re-synced.
-- setval sets the next auto-increment value to max(existing_id) + 1.
-- pg_get_serial_sequence finds the sequence name for a given column.
-- COALESCE returns 1 if the table is empty.
-- ===========================================
SELECT setval(pg_get_serial_sequence('"Customer"', 'customer_id'), COALESCE((SELECT MAX(customer_id) FROM "Customer"), 1));
SELECT setval(pg_get_serial_sequence('"Packages"', 'package_id'), COALESCE((SELECT MAX(package_id) FROM "Packages"), 1));
SELECT setval(pg_get_serial_sequence('"Timeline"', 'timeline_id'), COALESCE((SELECT MAX(timeline_id) FROM "Timeline"), 1));
SELECT setval(pg_get_serial_sequence('"Languages"', 'language_id'), COALESCE((SELECT MAX(language_id) FROM "Languages"), 1));
SELECT setval(pg_get_serial_sequence('"MinuteMen"', 'agent_id'), COALESCE((SELECT MAX(agent_id) FROM "MinuteMen"), 1));
SELECT setval(pg_get_serial_sequence('"Violations"', 'violation_id'), COALESCE((SELECT MAX(violation_id) FROM "Violations"), 1));
SELECT setval(pg_get_serial_sequence('"Booking"', 'booking_id'), COALESCE((SELECT MAX(booking_id) FROM "Booking"), 1));
SELECT setval(pg_get_serial_sequence('"Payments"', 'payment_id'), COALESCE((SELECT MAX(payment_id) FROM "Payments"), 1));
SELECT setval(pg_get_serial_sequence('"Identities"', 'identity_id'), COALESCE((SELECT MAX(identity_id) FROM "Identities"), 1));
SELECT setval(pg_get_serial_sequence('"Trip_Violations"', 'trip_violation_id'), COALESCE((SELECT MAX(trip_violation_id) FROM "Trip_Violations"), 1));
