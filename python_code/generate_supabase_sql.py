"""
generate_supabase_sql.py
Generates supabase_migration.sql from the local SQLite database.
This SQL script can be pasted into the Supabase SQL Editor to:
  1. Drop all existing cloud tables
  2. Recreate the full schema (with PostgreSQL-compatible types)
  3. Insert ALL data from the local SQLite database (including transactional records)
Use generate_supabase_reset.py instead if you only want to reset reference data.
"""
import sqlite3
import os

# DB_PATH: str — path to the local SQLite database to read from
DB_PATH = "time_travel.db"
# OUTPUT_SQL: str — name of the SQL file to generate
OUTPUT_SQL = "supabase_migration.sql"

# Main function that reads the SQLite schema and writes a full PostgreSQL migration script
def migrate():
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

    # Open the output SQL file for writing (UTF-8 encoding)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- Supabase Migration Script\n")
        f.write("-- Generated for PostgreSQL compatibility\n\n")

        # --- STEP 1: DROP TABLES ---
        # ordered_tables: List[str] — dependency-ordered list of table names
        # Drop in this order to avoid foreign key violations:
        #   Trip_Violations -> Identities -> Payments -> Booking -> ...
        # The tables Booking and Identities depend on others, so they are dropped first
        ordered_tables = [
            "Trip_Violations", "Identities", "Payments", "Booking",
            "Violations", "MinuteMen", "Languages", "Timeline", "Packages", "Customer"
        ]

        # Write DROP TABLE IF EXISTS ... CASCADE for each table in dependency order
        for table in ordered_tables:
            if table in tables:
                f.write(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;\n")
        f.write("\n")

        # --- STEP 2: CREATE TABLES ---
        # schema: Dict[str, str] — maps each table name to its PostgreSQL CREATE TABLE statement
        # SQLite to PostgreSQL type mapping used here:
        #   INTEGER PRIMARY KEY AUTOINCREMENT -> SERIAL PRIMARY KEY
        #   REAL                              -> DOUBLE PRECISION
        #   BOOLEAN                           -> BOOLEAN (SQLite stores 0/1, Postgres uses TRUE/FALSE)
        schema = {
            "Customer": """CREATE TABLE \"Customer\" (
    customer_id SERIAL PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    phone_num TEXT,
    address TEXT,
    birthdate TEXT,
    email TEXT,
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
    language_name TEXT
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

        # Write CREATE TABLE statements in creation order (independent tables first)
        # reversed(ordered_tables) gives: Customer, Packages, Timeline, ... Trip_Violations
        creation_order = reversed(ordered_tables)
        for table in creation_order:
            if table in schema:
                f.write(schema[table] + "\n\n")

        # --- STEP 3: INSERT ALL DATA ---
        # Unlike generate_supabase_reset.py, this script inserts ALL rows (not just reference data)
        f.write("-- Data Inclusion\n")
        # Iterate in same order as table creation (independent tables first)
        for table in reversed(ordered_tables):
            if table not in tables:
                continue

            # Fetch all rows in the table
            cursor.execute(f'SELECT * FROM "{table}"')
            rows = cursor.fetchall()
            if not rows:
                continue

            # Retrieve column names via SQLite PRAGMA
            # cols: List[str] — ordered list of column names
            cursor.execute(f'PRAGMA table_info("{table}")')
            cols = [col[1] for col in cursor.fetchall()]
            cols_str = ", ".join([f'"{c}"' for c in cols])

            for row in rows:
                # Build SQL-safe value strings for each column in the row
                values = []
                for val in row:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str):
                        # Escape single quotes to prevent SQL injection / syntax errors
                        safe_val = val.replace("'", "''")
                        values.append(f"'{safe_val}'")
                    elif isinstance(val, bool):
                        values.append("TRUE" if val else "FALSE")
                    else:
                        values.append(str(val))

                vals_str = ", ".join(values)
                f.write(f'INSERT INTO "{table}" ({cols_str}) VALUES ({vals_str});\n')
            f.write("\n")

    # Close the SQLite connection after reading is complete
    conn.close()
    print(f"Success! '{OUTPUT_SQL}' has been generated.")
    print("You can now copy its content into the Supabase SQL Editor.")

# Entry point — only runs when executed directly (not when imported)
if __name__ == "__main__":
    migrate()
