-- supabase_add_unique_constraint.sql
-- Run this in the Supabase SQL Editor to add a UNIQUE constraint to the Languages table.
-- This prevents duplicate language names from being inserted,
-- enabling ON CONFLICT (language_name) DO NOTHING to work correctly.

-- ALTER TABLE: modifies an existing table definition
-- ADD CONSTRAINT: names and creates a new UNIQUE constraint on language_name
ALTER TABLE "Languages" ADD CONSTRAINT "Languages_language_name_key" UNIQUE (language_name);
