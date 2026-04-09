"""
generate_supabase_reset.py
Generates supabase_reset.sql from the local SQLite database.
This SQL script can be run in the Supabase SQL Editor to:
  1. Drop all existing cloud tables
  2. Recreate the full schema
  3. Re-insert reference data (Packages, Languages, MinuteMen, Violations)
  4. Synchronize auto-increment sequences
WARNING: Running the output SQL will WIPE all cloud data.
"""
import sqlite3
import os

# DB_PATH: str — path to the local SQLite database to read from
DB_PATH = "time_travel.db"
# OUTPUT_SQL: str — name of the SQL file to generate
OUTPUT_SQL = "supabase_reset.sql"

# Main function that reads the SQLite schema and generates the PostgreSQL reset SQL
def create_reset_script():
    # Verify the source SQLite database exists before proceeding
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    # conn: sqlite3.Connection — connection to the local SQLite database
    conn = sqlite3.connect(DB_PATH)
    # cursor: sqlite3.Cursor — used to execute read queries
    cursor = conn.cursor()

    # Fetch all user-defined table names (exclude internal sqlite_ system tables)
    # tables: List[str]
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    # Open the output SQL file for writing (UTF-8 to handle special characters)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- ===========================================\n")
        f.write("-- SUPABASE FULL DATABASE RESET SCRIPT\n")
        f.write("-- WARNING: This deletes ALL cloud data and rebuilds\n")
        f.write("-- the entire schema from your local SQLite database.\n")
        f.write("-- ===========================================\n\n")

        # --- STEP 1: DROP TABLES ---
        # ordered_tables: List[str] — tables listed in reverse dependency order
        # (dependent tables like Trip_Violations first, independent like Customer last)
        # This order avoids foreign key constraint errors during CASCADE drops
        ordered_tables = [
            "Trip_Violations", "Identities", "Payments", "Booking",
            "Violations", "MinuteMen", "Languages", "Timeline", "Packages", "Customer"
        ]

        f.write("-- 1. DROP EXISTING TABLES\n")
        # Write a DROP TABLE IF EXISTS ... CASCADE statement for each table
        for table in ordered_tables:
            if table in tables:
                f.write(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;\n")
        f.write("\n")

        # --- STEP 2: CREATE TABLES ---
        # schema: Dict[str, str] — maps table name to its PostgreSQL CREATE TABLE statement
        # Key type mappings from SQLite to PostgreSQL:
        #   INTEGER PRIMARY KEY AUTOINCREMENT -> SERIAL PRIMARY KEY
        #   REAL                              -> DOUBLE PRECISION
        #   BOOLEAN                           -> BOOLEAN
        schema = {
            "Customer": """CREATE TABLE \"Customer\" (
    customer_id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    phone_num TEXT,
    address TEXT,
    birthdate TEXT,
    email TEXT UNIQUE,
    sex TEXT
);""",
            "Packages": """CREATE TABLE \"Packages\" (
    package_id SERIAL PRIMARY KEY,
    description TEXT UNIQUE,
    package_rate DOUBLE PRECISION
);""",
            "Timeline": """CREATE TABLE \"Timeline\" (
    timeline_id SERIAL PRIMARY KEY,
    timeline_year TEXT,
    map TEXT
);""",
            "Languages": """CREATE TABLE \"Languages\" (
    language_id SERIAL PRIMARY KEY,
    language_name TEXT UNIQUE
);""",
            "MinuteMen": """CREATE TABLE \"MinuteMen\" (
    agent_id SERIAL PRIMARY KEY,
    badge_number TEXT UNIQUE,
    agent_name TEXT
);""",
            "Violations": """CREATE TABLE \"Violations\" (
    violation_id SERIAL PRIMARY KEY,
    crime TEXT UNIQUE,
    penalty_description TEXT,
    fine_amount DOUBLE PRECISION
);""",
            "Booking": """CREATE TABLE \"Booking\" (
    booking_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES \"Customer\"(customer_id),
    package_id INTEGER REFERENCES \"Packages\"(package_id),
    timeline_id INTEGER REFERENCES \"Timeline\"(timeline_id),
    spawn_country TEXT,
    minutes INTEGER,
    insurance BOOLEAN,
    memory_reset BOOLEAN,
    total_price DOUBLE PRECISION,
    booking_languages TEXT,
    fame_level INTEGER,
    agent_id INTEGER REFERENCES \"MinuteMen\"(agent_id),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""",
            "Identities": """CREATE TABLE \"Identities\" (
    identity_id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    sex TEXT,
    fame_level INTEGER,
    booking_id INTEGER REFERENCES \"Booking\"(booking_id)
);""",
            "Payments": """CREATE TABLE \"Payments\" (
    payment_id SERIAL PRIMARY KEY,
    amount DOUBLE PRECISION,
    currency TEXT,
    method TEXT,
    customer_id INTEGER REFERENCES \"Customer\"(customer_id),
    booking_id INTEGER REFERENCES \"Booking\"(booking_id)
);""",
            "Trip_Violations": """CREATE TABLE \"Trip_Violations\" (
    trip_violation_id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES \"Booking\"(booking_id),
    violation_id INTEGER REFERENCES \"Violations\"(violation_id),
    occurrence_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""
        }

        f.write("-- 2. RECREATE TABLES\n")
        # Create tables in reverse dependency order (independent tables first)
        # reversed(ordered_tables) gives: Customer, Packages, ... Trip_Violations
        creation_order = reversed(ordered_tables)
        for table in creation_order:
            if table in schema:
                f.write(schema[table] + "\n\n")

        # --- STEP 3: INSERT REFERENCE DATA ONLY ---
        # We only seed the reference (lookup) tables — not transactional data
        # reference_tables: List[str] — only these tables get data inserted
        f.write("-- 3. INSERT LOCAL REFERENCE DATA ONLY\n")
        reference_tables = ["Packages", "Languages", "MinuteMen", "Violations"]
        for table in reversed(ordered_tables):
            if table not in tables or table not in reference_tables:
                continue

            # Fetch all rows from the SQLite table
            cursor.execute(f'SELECT * FROM "{table}"')
            rows = cursor.fetchall()
            if not rows:
                continue

            # Get the column names for the table via PRAGMA
            # cols: List[str] — column names in order
            cursor.execute(f'PRAGMA table_info("{table}")')
            cols = [col[1] for col in cursor.fetchall()]
            cols_str = ", ".join([f'"{c}"' for c in cols])

            # Track already-seen unique values to avoid duplicate INSERTs
            # seen_unique: Set[Any]
            seen_unique = set()

            for row in rows:
                # The unique column is always at index 1 for all reference tables:
                # Packages.description, Languages.language_name, MinuteMen.badge_number, Violations.crime
                unique_val = row[1]
                if unique_val in seen_unique:
                    continue
                seen_unique.add(unique_val)

                # Build a SQL-safe list of value strings
                values = []
                for val in row:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str):
                        # Escape single quotes by doubling them (SQL standard)
                        safe_val = val.replace("'", "''")
                        values.append(f"'{safe_val}'")
                    elif isinstance(val, bool):
                        values.append("TRUE" if val else "FALSE")
                    else:
                        values.append(str(val))

                vals_str = ", ".join(values)
                f.write(f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str});\n')
            f.write("\n")

        # --- STEP 4: SYNC SEQUENCES ---
        # After inserting rows with explicit IDs, the auto-increment sequence may be out of sync.
        # setval + pg_get_serial_sequence resets each sequence to max(existing_id)
        # to prevent primary key collisions on future inserts
        f.write("-- 4. SYNCHRONIZE AUTO-INCREMENT SEQUENCES\n")
        f.write("-- Prevents primary key collisions after manual data insertion\n")
        for table in reversed(ordered_tables):
            if table in tables:
                # Extract the primary key column name from the schema definition
                # pk_col: str — name of the SERIAL PRIMARY KEY column (e.g. "customer_id")
                pk_col = next((l.split()[0].strip() for l in schema[table].split('\n') if 'PRIMARY KEY' in l), None)
                if pk_col:
                    f.write(f"SELECT setval(pg_get_serial_sequence('\"{table}\"', '{pk_col}'), COALESCE((SELECT MAX({pk_col}) FROM \"{table}\"), 1));\n")

    # Close the SQLite connection
    conn.close()
    print(f"Success! '{OUTPUT_SQL}' has been generated.")
    print("WARNING: Running this in Supabase will completely WIPE and reset your cloud database!")

# Entry point — only runs when executed directly (not when imported)
if __name__ == "__main__":
    create_reset_script()
