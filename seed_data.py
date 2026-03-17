"""
seed_data.py
Generates 50 realistic fake bookings into the Time Travel database.
Run this after reset_db.py to populate the database with test data.
"""
import random
import os
from faker import Faker

try:
    from dotenv import load_dotenv
    import psycopg2
    HAS_DB_DRIVERS = True
    # Load environment variables if .env exists
    load_dotenv()
except ImportError:
    HAS_DB_DRIVERS = False

# Initialize faker object
# fake will randomly select from the Faker() package emails or names.
# Minutes spent or other aspects are randomly chosen from the list
fake = Faker()

# Configuration : number of trips and database name 
NUM_TRIPS = 50
DB_PATH   = "time_travel.db"

# Determine SQL placeholder type
PL = "%s" if (HAS_DB_DRIVERS and os.getenv("SUPABASE_DB_URL")) else "?"

def get_connection():
    db_url = os.getenv("SUPABASE_DB_URL")
    if HAS_DB_DRIVERS and db_url:
        return psycopg2.connect(db_url)
    import sqlite3
    return sqlite3.connect(DB_PATH)

# -------------------------------------------------------
# Shared reference data (must match DB pre-populated rows)
# -------------------------------------------------------

PACKAGES = {
    "Peasant Package": {"rate": 10.0,  "fame": False},
    "Quantum Query":   {"rate": 20.0,  "fame": True},
    "Monarch Mode":    {"rate": 50.0,  "fame": True},
}

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

BASE_LANGUAGES = [
    "Latin", "Ancient Greek", "Egyptian", "Sanskrit", "Old Norse",
    "Aramaic", "Old English", "Classical Chinese", "Japanese", "Spanish",
    "French", "German", "Italian", "Russian", "Hebrew",
]

SEXES = ["Male", "Female", "Other"]

# Random phonenumber generation
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
    base_fee   = PACKAGES[package_name]["rate"]
    base_price = minutes * base_fee
    identity_multiplier = 1 + (fame * 0.2) if fame else 1.0
    fame_extra = base_price * (identity_multiplier - 1)
    language_cost  = 50 * lang_count if package_name == "Quantum Query" else 0
    insurance_cost = 200 if insurance else 0
    memory_cost    = 100 if memory_reset else 0
    return base_price + fame_extra + language_cost + insurance_cost + memory_cost


# -------------------------------------------------------
# Main seed routine
# -------------------------------------------------------

# Connect to database 
conn   = get_connection()
cursor = conn.cursor()

# Fetch all pre-populated reference IDs
cursor.execute("SELECT agent_id, agent_name, badge_number FROM MinuteMen")
all_agents = cursor.fetchall()

cursor.execute("SELECT package_id, description FROM Packages")
pkg_map = {row[1]: row[0] for row in cursor.fetchall()}

cursor.execute("SELECT language_id, language_name FROM Languages")
lang_map = {row[1]: row[0] for row in cursor.fetchall()}

booked = 0
for _ in range(NUM_TRIPS):
    sex = random.choices(["Male", "Female", "Other"], weights=[49, 49, 2], k=1)[0]
    package_name   = random.choice(list(PACKAGES.keys()))
    fame           = random.randint(1, 5) if PACKAGES[package_name]["fame"] else 0
    minutes        = random.randint(15, 1440)
    timeline       = random.choice(TIMELINES)
    spawn_country  = fake.country()
    # Insurance & Memory Reset probabilities
    if package_name == "Peasant Package":
        insurance    = False
        memory_reset = random.choice([True, False])
    elif package_name == "Monarch Mode":
        # Monarchs usually take everything since it's "cheap" relative to the package
        insurance    = random.choices([True, False], weights=[90, 10])[0]
        memory_reset = random.choices([True, False], weights=[90, 10])[0]
    else:
        # Standard random for everything else
        insurance    = random.choice([True, False])
        memory_reset = random.choice([True, False])

    # Pick 0-3 languages only for Quantum Query (Monarch gets them free/stored same way)
    chosen_langs = []
    if package_name in ["Quantum Query", "Monarch Mode"]:
        sample_pool = [l for l in BASE_LANGUAGES if l in lang_map]
        chosen_langs = random.sample(sample_pool, k=random.randint(0, 3))

    booking_languages_str = ",".join(str(lang_map[l]) for l in chosen_langs)
    total_price = calculate_price(package_name, minutes, fame, insurance, memory_reset, len(chosen_langs))

    # ---- INSERT CUSTOMER ----
    if sex == "Male":
        first = fake.first_name_male()
    elif sex == "Female":
        first = fake.first_name_female()
    else:
        first = fake.first_name_nonbinary()

    last  = fake.last_name()
    email = fake.unique.email()
    phone = generate_phone()
    addr  = fake.street_address()
    dob   = fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()

    cursor.execute(f"""
        INSERT INTO Customer (first_name, last_name, phone_num, address, birthdate, email, sex)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL})
    """, (first, last, phone, addr, dob, email, sex))
    
    if os.getenv("SUPABASE_DB_URL"):
        # We need a different way to get IDs for multi-table inserts in Postgres
        # For simplicity in this script, we'll re-query or use RETURNING
        cursor.execute(f"SELECT customer_id FROM Customer WHERE email={PL}", (email,))
        customer_id = cursor.fetchone()[0]
    else:
        customer_id = cursor.lastrowid

    # ---- INSERT TIMELINE ----
    cursor.execute(f"INSERT INTO Timeline (timeline_year, map) VALUES ({PL}, {PL})", (timeline, spawn_country))
    if os.getenv("SUPABASE_DB_URL"):
        cursor.execute("SELECT MAX(timeline_id) FROM Timeline")
        timeline_id = cursor.fetchone()[0]
    else:
        timeline_id = cursor.lastrowid

    # ---- GET PACKAGE ID ----
    package_id = pkg_map.get(package_name)

    # ---- ASSIGN RANDOM MINUTEMAN ----
    agent = random.choice(all_agents)
    agent_id, agent_name, agent_badge = agent

    # ---- INSERT BOOKING ----
    booking_query = f"""
        INSERT INTO Booking
        (customer_id, package_id, timeline_id, spawn_country, minutes,
         insurance, memory_reset, total_price, booking_languages, fame_level, agent_id)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL})
    """
    if os.getenv("SUPABASE_DB_URL"):
        booking_query += " RETURNING booking_id"
        
    cursor.execute(booking_query, (customer_id, package_id, timeline_id, spawn_country,
          minutes, insurance, memory_reset, total_price,
          booking_languages_str, fame, agent_id))
          
    if os.getenv("SUPABASE_DB_URL"):
        booking_id = cursor.fetchone()[0]
    else:
        booking_id = cursor.lastrowid

    # ---- INSERT IDENTITY (non-Peasant only) ----
    if package_name != "Peasant Package":
        alias_first = fake.first_name_male() if sex == "Male" else fake.first_name_female() if sex == "Female" else fake.first_name_nonbinary()
        alias_last  = fake.last_name()
        cursor.execute(f"""
            INSERT INTO Identities (first_name, last_name, sex, fame_level, booking_id)
            VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
        """, (alias_first, alias_last, sex, fame, booking_id))

    # ---- INSERT PAYMENT ----
    currency_choice = random.choice(list(CURRENCY_RATES.keys()))
    currency_code   = currency_choice.split(' ')[0]
    rate            = CURRENCY_RATES[currency_choice]
    converted_total = total_price * rate
    
    method   = random.choice(["Visa", "MasterCard", "American Express", "Cash", "Twint"])
    
    cursor.execute(f"""
        INSERT INTO Payments (amount, currency, method, customer_id, booking_id)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
    """, (converted_total, currency_code, method, customer_id, booking_id))

    # ---- SIMULATE VIOLATION (1% chance) ----
    if random.random() < 0.01:
        cursor.execute("SELECT violation_id FROM Violations")
        all_v_ids = [r[0] for r in cursor.fetchall()]
        if all_v_ids:
            v_id = random.choice(all_v_ids)
            cursor.execute(f"""
                INSERT INTO Trip_Violations (booking_id, violation_id)
                VALUES ({PL}, {PL})
            """, (booking_id, v_id))

    booked += 1

conn.commit()
conn.close()

print(f"Done! {booked} fake trips inserted into '{DB_PATH}'.")
