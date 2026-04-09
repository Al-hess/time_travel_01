"""
seed_data.py
Generates 50 realistic fake bookings into the Time Travel database.
Run this after reset_db.py to populate the database with test data.
"""
import random
import os
from faker import Faker

# Attempt to import optional dependencies for Supabase (PostgreSQL) support
try:
    from dotenv import load_dotenv
    import psycopg2
    HAS_DB_DRIVERS = True
    # Load environment variables from .env file if it exists (sets SUPABASE_DB_URL etc.)
    load_dotenv()
except ImportError:
    # If psycopg2 or dotenv are not installed, fall back to SQLite only
    HAS_DB_DRIVERS = False

# Initialize the Faker instance for generating realistic fake data
# fake: Faker object — used to generate names, emails, addresses, dates
fake = Faker()

# Configuration constants
# NUM_TRIPS: int — number of fake bookings to generate
# DB_PATH: str — path to the local SQLite database file
NUM_TRIPS = 50
DB_PATH   = "time_travel.db"

# SQL placeholder character differs between databases
# PostgreSQL uses %s, SQLite uses ?
# PL: str
PL = "%s" if (HAS_DB_DRIVERS and os.getenv("SUPABASE_DB_URL")) else "?"

# Returns a live database connection (SQLite or PostgreSQL depending on env)
def get_connection():
    db_url = os.getenv("SUPABASE_DB_URL")
    if HAS_DB_DRIVERS and db_url:
        # Connect to Supabase PostgreSQL using the connection URL
        return psycopg2.connect(db_url)
    import sqlite3
    # Fall back to local SQLite database
    return sqlite3.connect(DB_PATH)

# -------------------------------------------------------
# Shared reference data (must match DB pre-populated rows)
# -------------------------------------------------------

# PACKAGES: Dict[str, Dict[str, Union[float, bool]]]
# Maps package name to its per-minute rate and whether identity/fame is applicable
PACKAGES = {
    "Peasant Package": {"rate": 10.0,  "fame": False},
    "Quantum Query":   {"rate": 20.0,  "fame": True},
    "Monarch Mode":    {"rate": 50.0,  "fame": True},
}

# CURRENCY_RATES: Dict[str, float]
# Conversion multipliers from USD to the target currency
CURRENCY_RATES = {
    "USD ($)": 1.0,
    "EUR (€)": 0.92,
    "GBP (£)": 0.78,
    "JPY (¥)": 150.0,
    "CNY (¥)": 7.19,
    "CHF (Fr)": 0.88,
    "BTC (Bitcoin)": 0.000015,
    "ETH (Ethereum)": 0.00032,
    "CC (ChronoCredits)": 10.0
}

# TIMELINES: List[str]
# The historical periods available as destination options
TIMELINES = [
    "Dinosaurs Era (-65000000)",
    "Stone Age (-500000)",
    "Ancient Egypt (-3000)",
    "Mesopotamia (-2500)",
    "Ancient Greece (-500)",
    "Roman Republic (-200)",
    "Roman Empire (100)",
    "Han Dynasty China (100)",
    "Viking Age (800)",
    "Medieval Europe (1200)",
    "Mongol Empire (1250)",
    "Black Death (1350)",
    "Renaissance Italy (1450)",
    "Age of Exploration (1500)",
    "French Revolution (1789)",
    "Industrial Revolution (1800)",
    "American Civil War (1865)",
    "Belle Epoque (1900)",
    "World War I (1916)",
    "Roaring Twenties (1925)",
    "World War II (1940)",
    "Cold War (1960)",
    "Moon Landing (1969)",
    "Fall of Berlin Wall (1989)",
]

# BASE_LANGUAGES: List[str]
# A subset of languages used for random language assignment during seeding
BASE_LANGUAGES = [
    "Latin", "Ancient Greek", "Egyptian", "Sanskrit", "Old Norse",
    "Aramaic", "Old English", "Classical Chinese", "Japanese", "Spanish",
    "French", "German", "Italian", "Russian", "Hebrew",
]

# SEXES: List[str]
# Gender options used for customer and identity generation
SEXES = ["Male", "Female", "Other"]

# Generates a random international phone number in +xx xx xxx xx xx format
# Returns: str
def generate_phone():
    """
    Generates a realistic-looking international phone number.
    Returns:
        str: A string in the format +xx xx xxx xx xx.
    """
    cc  = random.randint(10, 99)
    p1  = random.randint(10, 99)
    p2  = random.randint(100, 999)
    p3  = random.randint(10, 99)
    p4  = random.randint(10, 99)
    return f"+{cc} {p1} {p2} {p3} {p4}"


# Calculates the total trip cost based on package, duration, fame level, and add-ons
# Returns: float (total cost in USD)
def calculate_price(package_name, minutes, fame, insurance, memory_reset, lang_count):
    """
    Calculates the total cost of a booking based on various parameters.
    Args:
        package_name (str): Name of the selected package.
        minutes (int): Duration of the trip in minutes.
        fame (int): Selected fame level (0-5).
        insurance (bool): Whether insurance was selected.
        memory_reset (bool): Whether memory reset was selected.
        lang_count (int): Number of languages purchased.
    Returns:
        float: The calculated total price.
    """
    # Base cost = duration (minutes) multiplied by the package rate
    base_fee   = PACKAGES[package_name]["rate"]
    base_price = minutes * base_fee
    # Identity multiplier increases price based on fame level (1 + fame * 20%)
    identity_multiplier = 1 + (fame * 0.2) if fame else 1.0
    fame_extra = base_price * (identity_multiplier - 1)
    # Language cost only applies to Quantum Query (50 USD each); Monarch gets them free
    language_cost  = 50 * lang_count if package_name == "Quantum Query" else 0
    insurance_cost = 200 if insurance else 0
    memory_cost    = 100 if memory_reset else 0
    return base_price + fame_extra + language_cost + insurance_cost + memory_cost


# -------------------------------------------------------
# Main seed routine
# -------------------------------------------------------

# Connect to the database (SQLite or PostgreSQL depending on environment)
conn   = get_connection()
cursor = conn.cursor()

# Fetch all pre-populated reference IDs needed for foreign key assignment
# all_agents: List[Tuple[int, str, str]] - (agent_id, agent_name, badge_number)
cursor.execute('SELECT agent_id, agent_name, badge_number FROM "MinuteMen"')
all_agents = cursor.fetchall()

# pkg_map: Dict[str, int] - maps package name to its primary key ID
cursor.execute('SELECT package_id, description FROM "Packages"')
pkg_map = {row[1]: row[0] for row in cursor.fetchall()}

# lang_map: Dict[str, int] - maps language name to its primary key ID
cursor.execute('SELECT language_id, language_name FROM "Languages"')
lang_map = {row[1]: row[0] for row in cursor.fetchall()}

# booked: int - counter of successfully inserted trips
booked = 0
for _ in range(NUM_TRIPS):
    # Pick a random sex with realistic weights (49% M, 49% F, 2% Other)
    sex = random.choices(["Male", "Female", "Other"], weights=[49, 49, 2], k=1)[0]
    package_name   = random.choice(list(PACKAGES.keys()))
    # fame is only relevant for non-Peasant packages
    fame           = random.randint(1, 5) if PACKAGES[package_name]["fame"] else 0
    # minutes: int — trip duration between 15 minutes and 24 hours
    minutes        = random.randint(15, 1440)
    timeline       = random.choice(TIMELINES)
    # spawn_country: str — randomly generated country name via Faker
    spawn_country  = fake.country()

    # Insurance & Memory Reset probabilities differ by package
    if package_name == "Peasant Package":
        # Peasant travellers cannot buy insurance
        insurance    = False
        memory_reset = random.choice([True, False])
    elif package_name == "Monarch Mode":
        # Monarchs usually take everything since it's cheap relative to the package
        insurance    = random.choices([True, False], weights=[90, 10])[0]
        memory_reset = random.choices([True, False], weights=[90, 10])[0]
    else:
        # Standard random selection for Quantum Query
        insurance    = random.choice([True, False])
        memory_reset = random.choice([True, False])

    # Pick 0-3 languages only for Quantum Query or Monarch Mode
    # chosen_langs: List[str] — language names selected from BASE_LANGUAGES
    chosen_langs = []
    if package_name in ["Quantum Query", "Monarch Mode"]:
        # Filter to only languages that exist in the database
        sample_pool = [l for l in BASE_LANGUAGES if l in lang_map]
        chosen_langs = random.sample(sample_pool, k=random.randint(0, 3))

    # Build a comma-separated string of language IDs for the booking record
    booking_languages_str = ",".join(str(lang_map[l]) for l in chosen_langs)
    # total_price: float — computed using the calculate_price function
    total_price = calculate_price(package_name, minutes, fame, insurance, memory_reset, len(chosen_langs))

    # ---- INSERT CUSTOMER ----
    # Generate a sex-appropriate fake first name using Faker
    if sex == "Male":
        first = fake.first_name_male()
    elif sex == "Female":
        first = fake.first_name_female()
    else:
        first = fake.first_name_nonbinary()

    last  = fake.last_name()
    # fake.unique.email() guarantees no duplicate email addresses
    email = fake.unique.email()
    phone = generate_phone()
    addr  = fake.street_address()
    # dob: str — ISO format date string for date of birth
    dob   = fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()

    cursor.execute(f"""
        INSERT INTO "Customer" (first_name, last_name, phone_num, address, birthdate, email, sex)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL})
    """, (first, last, phone, addr, dob, email, sex))

    if os.getenv("SUPABASE_DB_URL"):
        # PostgreSQL does not support lastrowid; re-query using the unique email
        cursor.execute(f'SELECT customer_id FROM "Customer" WHERE email={PL}', (email,))
        customer_id = cursor.fetchone()[0]
    else:
        # SQLite provides the last inserted row ID directly
        customer_id = cursor.lastrowid

    # ---- INSERT TIMELINE ----
    # Each booking gets its own Timeline entry (era + spawn country as map reference)
    cursor.execute(f'INSERT INTO "Timeline" (timeline_year, map) VALUES ({PL}, {PL})', (timeline, spawn_country))
    if os.getenv("SUPABASE_DB_URL"):
        # Re-query to get the new timeline_id in PostgreSQL
        cursor.execute('SELECT MAX(timeline_id) FROM "Timeline"')
        timeline_id = cursor.fetchone()[0]
    else:
        timeline_id = cursor.lastrowid

    # ---- GET PACKAGE ID ----
    # Look up the integer primary key for the selected package name
    package_id = pkg_map.get(package_name)

    # ---- ASSIGN RANDOM MINUTEMAN ----
    # Select a random agent from the pre-fetched list
    agent = random.choice(all_agents)
    # Unpack the agent tuple into individual variables
    agent_id, agent_name, agent_badge = agent

    # ---- INSERT BOOKING ----
    # Build the INSERT query dynamically (RETURNING clause needed for PostgreSQL)
    booking_query = f"""
        INSERT INTO "Booking"
        (customer_id, package_id, timeline_id, spawn_country, minutes,
         insurance, memory_reset, total_price, booking_languages, fame_level, agent_id)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL})
    """
    if os.getenv("SUPABASE_DB_URL"):
        # RETURNING booking_id fetches the new ID immediately without a second query
        booking_query += " RETURNING booking_id"

    cursor.execute(booking_query, (customer_id, package_id, timeline_id, spawn_country,
          minutes, insurance, memory_reset, total_price,
          booking_languages_str, fame, agent_id))

    if os.getenv("SUPABASE_DB_URL"):
        booking_id = cursor.fetchone()[0]
    else:
        booking_id = cursor.lastrowid

    # ---- INSERT IDENTITY (non-Peasant only) ----
    # Peasant travellers have no identity — they are in ghost mode
    if package_name != "Peasant Package":
        # Generate a fake alias that matches the traveler's sex
        alias_first = fake.first_name_male() if sex == "Male" else fake.first_name_female() if sex == "Female" else fake.first_name_nonbinary()
        alias_last  = fake.last_name()
        cursor.execute(f"""
            INSERT INTO "Identities" (first_name, last_name, sex, fame_level, booking_id)
            VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
        """, (alias_first, alias_last, sex, fame, booking_id))

    # ---- INSERT PAYMENT ----
    # Pick a random currency and convert the USD price
    currency_choice = random.choice(list(CURRENCY_RATES.keys()))
    # currency_code: str — short code extracted from the currency label (e.g. "USD")
    currency_code   = currency_choice.split(' ')[0]
    # rate: float — conversion multiplier from USD to the chosen currency
    rate            = CURRENCY_RATES[currency_choice]
    # converted_total: float — final price in the chosen currency
    converted_total = total_price * rate

    # method: str — randomly selected payment method
    method   = random.choice(["Visa", "MasterCard", "American Express", "Cash", "Twint"])

    cursor.execute(f"""
        INSERT INTO "Payments" (amount, currency, method, customer_id, booking_id)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
    """, (converted_total, currency_code, method, customer_id, booking_id))

    # ---- SIMULATE VIOLATION (1% chance) ----
    # Randomly trigger a violation event with a 1% probability per booking
    if random.random() < 0.01:
        # Fetch all violation IDs from the catalog
        cursor.execute('SELECT violation_id FROM "Violations"')
        all_v_ids = [r[0] for r in cursor.fetchall()]
        if all_v_ids:
            # Assign one random violation to this booking
            v_id = random.choice(all_v_ids)
            cursor.execute(f"""
                INSERT INTO "Trip_Violations" (booking_id, violation_id)
                VALUES ({PL}, {PL})
            """, (booking_id, v_id))

    booked += 1

# Save all changes and close the database connection
conn.commit()
conn.close()

print(f"Done! {booked} fake trips inserted into '{DB_PATH}'.")
