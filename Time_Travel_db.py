# Time Travel Database creation script 
import sqlite3

conn = sqlite3.connect("time_travel.db")
cursor = conn.cursor()

# --- DROP TABLES (for clean reset) ---
# We drop tables in reverse order of dependencies to avoid foreign key issues
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

# This script initializes the database schema and populates reference tables.
# It ensures all required tables exist and contains the base data for packages,
# languages, agents (MinuteMen), and violation rules.

# =========================
# CUSTOMER
# =========================
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

for lang in base_languages:
    cursor.execute(
        "INSERT OR IGNORE INTO Languages (language_name) SELECT ?", 
        (lang,)
    )

# =========================
# PREPOPULATE TIMELINE
# =========================
# Predefined timeline destinations
timelines = [
    ("Dinosaurs Era", "-65000000"),
    ("Stone Age", "-500000"),
]

for timeline_year, map_data in timelines:
    cursor.execute(
        "INSERT OR IGNORE INTO Timeline (timeline_year, map) VALUES (?, ?)",
        (timeline_year, map_data)
    )

# =========================
# PREPOPULATE PACKAGES
# =========================
base_packages = [
    ("Peasant Package", 10.0),
    ("Quantum Query", 20.0),
    ("Monarch Mode", 50.0)
]

for pkg_name, rate in base_packages:
    cursor.execute(
        "INSERT OR IGNORE INTO Packages (description, package_rate) VALUES (?, ?)",
        (pkg_name, rate)
    )

# =========================
# PREPOPULATE MINUTEMEN
# =========================
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

for badge, name in minutemen_agents:
    cursor.execute(
        "INSERT OR IGNORE INTO MinuteMen (badge_number, agent_name) VALUES (?, ?)",
        (badge, name)
    )

# =========================
# PREPOPULATE VIOLATIONS
# =========================
catastrophic_crimes = [
    ("Murder", "Immediate timeline termination, final warning.", 5000.0),
    ("Genocide (or attempted)", "Immediate timeline termination, permanent ban.", 50000.0),
    ("Enslavement", "Immediate timeline termination, permanent ban.", 15000.0),
    ("Rape / Sexual misconduct", "Immediate timeline termination, permanent ban, report to authorities.", 10000.0),
]

for crime, penalty, fine in catastrophic_crimes:
    cursor.execute(
        "INSERT OR IGNORE INTO Violations (crime, penalty_description, fine_amount) VALUES (?, ?, ?)",
        (crime, penalty, fine)
    )

conn.commit()
conn.close()

print("All tables created successfully.")


# Check if tables exist  
conn = sqlite3.connect("time_travel.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

cursor.execute("SELECT * FROM Customer")
print(cursor.fetchall()) 