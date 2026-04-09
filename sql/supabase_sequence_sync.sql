-- supabase_sequence_sync.sql
-- Run this script in the Supabase SQL Editor to synchronize auto-increment sequences.
-- This is required after manually inserting rows with explicit primary key values,
-- because PostgreSQL sequences are not updated by explicit INSERT statements.
--
-- pg_get_serial_sequence(table, column): returns the name of the sequence linked to a SERIAL column
-- setval(sequence, value): sets the sequence's next value to value + 1
-- COALESCE(MAX(id), 1): returns 1 if the table is empty, otherwise the current max ID

-- Sync sequence for the Customer table (primary key: customer_id)
SELECT setval(pg_get_serial_sequence('"Customer"', 'customer_id'), COALESCE((SELECT MAX(customer_id) FROM "Customer"), 1));

-- Sync sequence for the Packages table (primary key: package_id)
SELECT setval(pg_get_serial_sequence('"Packages"', 'package_id'), COALESCE((SELECT MAX(package_id) FROM "Packages"), 1));

-- Sync sequence for the Timeline table (primary key: timeline_id)
SELECT setval(pg_get_serial_sequence('"Timeline"', 'timeline_id'), COALESCE((SELECT MAX(timeline_id) FROM "Timeline"), 1));

-- Sync sequence for the Languages table (primary key: language_id)
SELECT setval(pg_get_serial_sequence('"Languages"', 'language_id'), COALESCE((SELECT MAX(language_id) FROM "Languages"), 1));

-- Sync sequence for the MinuteMen table (primary key: agent_id)
SELECT setval(pg_get_serial_sequence('"MinuteMen"', 'agent_id'), COALESCE((SELECT MAX(agent_id) FROM "MinuteMen"), 1));

-- Sync sequence for the Violations table (primary key: violation_id)
SELECT setval(pg_get_serial_sequence('"Violations"', 'violation_id'), COALESCE((SELECT MAX(violation_id) FROM "Violations"), 1));

-- Sync sequence for the Booking table (primary key: booking_id)
SELECT setval(pg_get_serial_sequence('"Booking"', 'booking_id'), COALESCE((SELECT MAX(booking_id) FROM "Booking"), 1));

-- Sync sequence for the Identities table (primary key: identity_id)
SELECT setval(pg_get_serial_sequence('"Identities"', 'identity_id'), COALESCE((SELECT MAX(identity_id) FROM "Identities"), 1));

-- Sync sequence for the Payments table (primary key: payment_id)
SELECT setval(pg_get_serial_sequence('"Payments"', 'payment_id'), COALESCE((SELECT MAX(payment_id) FROM "Payments"), 1));

-- Sync sequence for the Trip_Violations table (primary key: trip_violation_id)
SELECT setval(pg_get_serial_sequence('"Trip_Violations"', 'trip_violation_id'), COALESCE((SELECT MAX(trip_violation_id) FROM "Trip_Violations"), 1));
