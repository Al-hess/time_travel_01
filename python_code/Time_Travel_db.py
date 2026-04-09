# Time Travel Database creation script
# This script initializes the database schema and populates reference tables.
# It ensures all required tables exist and contains the base data for packages,
# languages, agents (MinuteMen), and violation rules.

import sqlite3

# Open (or create) a connection to the SQLite database file
# conn: sqlite3.Connection object
conn = sqlite3.connect("time_travel.db")

# Create a cursor to execute SQL statements
# cursor: sqlite3.Cursor object
cursor = conn.cursor()

# --- DROP TABLES (for clean reset) ---
# We drop tables in reverse order of dependencies to avoid foreign key issues.
# Tables that reference other tables (via FOREIGN KEY) must be dropped first.
cursor.execute("DROP TABLE IF EXISTS Trip_Violations")
cursor.execute("DROP TABLE IF EXISTS Identities")
cursor.execute("DROP TABLE IF EXISTS Payments")
cursor.execute("DROP TABLE IF EXISTS Booking")
cursor.execute("DROP TABLE IF EXISTS Violations")
cursor.execute("DROP TABLE IF EXISTS MinuteMen")
cursor.execute("DROP TABLE IF EXISTS Languages")
cursor.execute("DROP TABLE IF EXISTS Timeline")
cursor.execute("DROP TABLE IF EXISTS Packages")
cursor.execute("DROP TABLE IF EXISTS Customer")

# =========================
# CUSTOMER
# =========================
# Stores personal details of each traveler.
# customer_id: INTEGER (auto-incremented primary key)
# first_name, last_name, phone_num, address, birthdate, email, sex: TEXT
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    phone_num TEXT,
    address TEXT,
    birthdate TEXT,
    email TEXT,
    sex TEXT
)
""")

# =========================
# PACKAGES
# =========================
# Available time travel packages with a daily rate per minute.
# package_id: INTEGER (auto-incremented primary key)
# description: TEXT (unique name of the package)
# package_rate: REAL (price per minute in USD)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Packages (
    package_id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT UNIQUE,
    package_rate REAL
)
""")

# =========================
# TIMELINE
# =========================
# Stores the historical period (era) that a traveler visits.
# timeline_id: INTEGER (auto-incremented primary key)
# timeline_year: TEXT (label such as "Roman Empire (100)")
# map: TEXT (numeric year used as map reference, e.g. "-65000000")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Timeline (
    timeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeline_year TEXT,
    map TEXT
)
""")

# =========================
# LANGUAGES
# =========================
# Catalog of historical and modern languages available for purchase.
# language_id: INTEGER (auto-incremented primary key)
# language_name: TEXT
cursor.execute("""
CREATE TABLE IF NOT EXISTS Languages (
    language_id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_name TEXT
)
""")

# =========================
# BOOKING (CENTRAL TABLE)
# =========================
# This table stores every trip transaction, linking customers, timelines,
# packages, and the agents assigned to monitor them.
# booking_id: INTEGER (auto-incremented primary key)
# customer_id, package_id, timeline_id, agent_id: INTEGER (foreign keys)
# spawn_country: TEXT (where the traveler materializes)
# minutes: INTEGER (duration of the trip)
# insurance, memory_reset: BOOLEAN (add-on options)
# total_price: REAL (final price in USD)
# booking_languages: TEXT (comma-separated language IDs)
# fame_level: INTEGER (social status level 1-5)
# booking_date: TIMESTAMP (auto-filled with current UTC time)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Booking (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER, 
    package_id INTEGER,
    timeline_id INTEGER,
    spawn_country TEXT,
    minutes INTEGER,
    insurance BOOLEAN,
    memory_reset BOOLEAN,
    total_price REAL,
    booking_languages TEXT,
    fame_level INTEGER,
    agent_id INTEGER,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY(package_id) REFERENCES Packages(package_id),
    FOREIGN KEY(timeline_id) REFERENCES Timeline(timeline_id),
    FOREIGN KEY(agent_id) REFERENCES MinuteMen(agent_id)
)
""")


# =========================
# IDENTITIES
# =========================
# Fake alias generated for travelers on non-Peasant packages.
# identity_id: INTEGER (auto-incremented primary key)
# first_name, last_name, sex: TEXT (generated alias)
# fame_level: INTEGER (mirrors the booking's fame level)
# booking_id: INTEGER (foreign key linking to Booking)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Identities (
    identity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    sex TEXT,
    fame_level INTEGER,
    booking_id INTEGER,
    FOREIGN KEY(booking_id) REFERENCES Booking(booking_id)
)
""")

# =========================
# PAYMENTS
# =========================
# Records the financial transaction associated with each booking.
# payment_id: INTEGER (auto-incremented primary key)
# amount: REAL (converted total in the selected currency)
# currency: TEXT (e.g. "USD", "BTC")
# method: TEXT (e.g. "Visa", "Cash")
# customer_id, booking_id: INTEGER (foreign keys)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    currency TEXT,
    method TEXT,
    customer_id INTEGER,
    booking_id INTEGER,
    FOREIGN KEY(customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY(booking_id) REFERENCES Booking(booking_id)
)
""")

# =========================
# MINUTEMEN
# =========================
# TimeCorp agents assigned to monitor traveler activity.
# agent_id: INTEGER (auto-incremented primary key)
# badge_number: TEXT (unique badge identifier, e.g. "MM-007")
# agent_name: TEXT
cursor.execute("""
CREATE TABLE IF NOT EXISTS MinuteMen (
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_number TEXT UNIQUE,
    agent_name TEXT
)
""")

# =========================
# VIOLATIONS CATALOG
# =========================
# Reference table of prohibited actions and their consequences.
# violation_id: INTEGER (auto-incremented primary key)
# crime: TEXT (unique description of the offense)
# penalty_description: TEXT (consequence for the traveler)
# fine_amount: REAL (monetary fine in USD)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    crime TEXT UNIQUE,
    penalty_description TEXT,
    fine_amount REAL
)
""")

# =========================
# TRIP VIOLATIONS (Bridge Table)
# =========================
# Many-to-many bridge table linking bookings to violations.
# trip_violation_id: INTEGER (auto-incremented primary key)
# booking_id, violation_id: INTEGER (foreign keys)
# occurrence_date: TIMESTAMP (auto-filled with current UTC time)
cursor.execute("""
CREATE TABLE IF NOT EXISTS Trip_Violations (
    trip_violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    violation_id INTEGER,
    occurrence_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(booking_id) REFERENCES Booking(booking_id),
    FOREIGN KEY(violation_id) REFERENCES Violations(violation_id)
)
""")

# =========================
# PREPOPULATE LANGUAGES
# =========================
# Adding a diverse set of historical and modern languages to the catalog.
# base_languages: List[str] - language names to insert into the Languages table
base_languages = [
    "Sumerian", "Akkadian", "Egyptian", "Hittite", "Elamite",
    "Sanskrit", "Prakrit", "Pali", "Old Persian", "Avestan",
    "Ancient Greek", "Latin", "Etruscan", "Phoenician", "Aramaic",
    "Hebrew", "Ugaritic", "Coptic", "Old Church Slavonic", "Gothic",
    "Old English", "Middle English", "Modern English", "Old Norse", "Icelandic",
    "Old High German", "Middle High German", "Modern German", "Yiddish", "Dutch",
    "Old French", "Middle French", "Modern French", "Occitan", "Catalan",
    "Italian", "Sicilian", "Spanish", "Portuguese", "Galician",
    "Romanian", "Dacian", "Albanian", "Irish", "Scottish Gaelic",
    "Welsh", "Breton", "Cornish", "Manx", "Basque",
    "Finnish", "Estonian", "Hungarian", "Maltese", "Lithuanian",
    "Latvian", "Prussian", "Russian", "Ukrainian",
    "Belarusian", "Polish", "Czech", "Slovak", "Serbo-Croatian",
    "Bulgarian", "Macedonian", "Slovene", "Greek", "Armenian",
    "Georgian", "Persian", "Kurdish", "Pashto", "Balochi",
    "Urdu", "Hindi", "Bengali", "Punjabi", "Marathi",
    "Gujarati", "Tamil", "Telugu", "Kannada", "Malayalam",
    "Sinhalese", "Thai", "Lao", "Khmer", "Burmese",
    "Chinese", "Classical Chinese", "Japanese", "Korean", "Vietnamese",
    "Tibetan", "Mongolian", "Turkish", "Uzbek", "Kazakh",
    "Azerbaijani", "Turkmen", "Tatar", "Yakut", "Chuvash"
]

# INSERT OR IGNORE skips insertion if the language already exists (avoids duplicates)
for lang in base_languages:
    cursor.execute(
        "INSERT OR IGNORE INTO Languages (language_name) SELECT ?", 
        (lang,)
    )

# =========================
# PREPOPULATE TIMELINE
# =========================
# Predefined timeline destinations available to travelers.
# timelines: List[Tuple[str, str]] - (era name, numeric year string)
timelines = [
    ("Dinosaurs Era", "-65000000"),
    ("Stone Age", "-500000"),
]

# Each tuple unpacks as (timeline_year, map_data)
for timeline_year, map_data in timelines:
    cursor.execute(
        "INSERT OR IGNORE INTO Timeline (timeline_year, map) VALUES (?, ?)",
        (timeline_year, map_data)
    )

# =========================
# PREPOPULATE PACKAGES
# =========================
# The three available travel packages with their per-minute USD rate.
# base_packages: List[Tuple[str, float]] - (package name, rate per minute)
base_packages = [
    ("Peasant Package", 10.0),
    ("Quantum Query", 20.0),
    ("Monarch Mode", 50.0)
]

# Each tuple unpacks as (pkg_name, rate)
for pkg_name, rate in base_packages:
    cursor.execute(
        "INSERT OR IGNORE INTO Packages (description, package_rate) VALUES (?, ?)",
        (pkg_name, rate)
    )

# =========================
# PREPOPULATE MINUTEMEN
# =========================
# Pre-assigned TimeCorp agents available for trip monitoring.
# minutemen_agents: List[Tuple[str, str]] - (badge_number, agent_name)
minutemen_agents = [
    ("MM-001", "Agent K"),
    ("MM-007", "Agent Vance"),
    ("MM-009", "Agent Weaver"),
    ("MM-012", "Agent Thorne"),
    ("MM-042", "Agent Sterling"),
    ("MM-088", "Agent Cross"),
    ("MM-099", "Agent Blackwood"),
    ("MM-101", "Agent Mercer"),
    ("MM-314", "Agent Pi"),
    ("MM-999", "Agent Alpha")
]

# Each tuple unpacks as (badge, name)
for badge, name in minutemen_agents:
    cursor.execute(
        "INSERT OR IGNORE INTO MinuteMen (badge_number, agent_name) VALUES (?, ?)",
        (badge, name)
    )

# =========================
# PREPOPULATE VIOLATIONS
# =========================
# Catalog of prohibited acts with associated fines and penalties.
# catastrophic_crimes: List[Tuple[str, str, float]] - (crime, penalty_description, fine_amount)
catastrophic_crimes = [
    ("Murder", "Immediate timeline termination, final warning.", 5000.0),
    ("Genocide (or attempted)", "Immediate timeline termination, permanent ban.", 50000.0),
    ("Enslavement", "Immediate timeline termination, permanent ban.", 15000.0),
    ("Rape / Sexual misconduct", "Immediate timeline termination, permanent ban, report to authorities.", 10000.0),
]

# Each tuple unpacks as (crime, penalty, fine)
for crime, penalty, fine in catastrophic_crimes:
    cursor.execute(
        "INSERT OR IGNORE INTO Violations (crime, penalty_description, fine_amount) VALUES (?, ?, ?)",
        (crime, penalty, fine)
    )

# Commit all changes and close the connection
conn.commit()
conn.close()

print("All tables created successfully.")


# Check if tables exist
# Reconnect to verify the tables were created
conn = sqlite3.connect("time_travel.db")
cursor = conn.cursor()

# Query the sqlite_master table to list all user-created tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# Confirm the Customer table is empty (freshly created)
cursor.execute("SELECT * FROM Customer")
print(cursor.fetchall())