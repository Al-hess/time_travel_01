# streamlit_app.py
# Main Streamlit application for the LevarT Time Travel booking platform.
# Provides a user interface for booking trips and viewing analytics.
# Connects to SQLite (local) or PostgreSQL via Supabase (cloud) based on environment.

# Import standard and third-party packages
import streamlit as st
from datetime import date
import sqlite3
import os
import random
import pandas as pd
import plotly.express as px
import plotly as pl
from faker import Faker

# Attempt to load optional packages for Supabase (PostgreSQL) connectivity
try:
    from dotenv import load_dotenv
    import psycopg2
    HAS_DB_DRIVERS = True
    # Load .env file to make SUPABASE_DB_URL available via os.getenv()
    load_dotenv()
except ImportError:
    # psycopg2 / dotenv not installed — fall back to SQLite only
    HAS_DB_DRIVERS = False

# fake: Faker instance — used to generate alias names for traveler identities
fake = Faker()

# PL: str — SQL placeholder character
# PostgreSQL uses %s, SQLite uses ?
PL = "%s" if (HAS_DB_DRIVERS and os.getenv("SUPABASE_DB_URL")) else "?"

# T_VAL / F_VAL: str — Boolean literal representation per database
# PostgreSQL: TRUE / FALSE | SQLite: 1 / 0
T_VAL = "TRUE" if (HAS_DB_DRIVERS and os.getenv("SUPABASE_DB_URL")) else "1"
F_VAL = "FALSE" if (HAS_DB_DRIVERS and os.getenv("SUPABASE_DB_URL")) else "0"

# get_connection: function — returns a live database connection
# Checks SUPABASE_DB_URL to decide between PostgreSQL and SQLite
def get_connection():
    """
    Establishes a connection to the database.
    Checks for SUPABASE_DB_URL environment variable to connect to PostgreSQL.
    Otherwise, defaults to local SQLite 'time_travel.db'.
    """
    db_url = os.getenv("SUPABASE_DB_URL")

    if HAS_DB_DRIVERS and db_url:
        # Connect to Supabase using psycopg2 with the full connection URL
        conn = psycopg2.connect(db_url)
        return conn
    else:
        # Fall back to local SQLite database file
        db_path = "time_travel.db"
        conn = sqlite3.connect(db_path)
        return conn

# Configure the Streamlit page (title, icon, layout)
st.set_page_config(page_title="LevarT EmiT - Time Travel", page_icon="⏳", layout="wide")

st.title("⏳ LevarT  - Time Travel")
st.write("### The Future of Tourism.")
st.caption("Travel across timelines safely, legally, and without butterfly effects.")

st.divider()

# Create 2 main tabs: booking form and analytics dashboard
tab_booking, tab_analytics = st.tabs(["Book a Trip", "Analytics"])

# Expander sections describing the company and legal conditions
with st.expander("How it works"):
    st.write(""" Levart creates a copy of the timeline you wish to visit. This method makes sure that the trip is safe and that there are no effects on our reality. Our MinuteMen agents monitor your trips and can intervene in case of any emergency. Once the trip is over, the timeline is pruned.
    """)
with st.expander("Requirements to Book a Trip"):
    st.write(""" Physical and psychological requirements:
    - Must be at least 18 years old
    - Must be in good health (no serious medical conditions, pregnancies...)
    - Must be mentally stable
    - Must be able to handle the stress of time travel
    """)
with st.expander("Legal considerations"):
    st.write("""The person traveling must read the conditions of travel and accept them before booking. Breach of the violations mentioned in the legal document result in penalties and may lead to legal consequences.
    Any crime against human dignity or life will not be tolerated and will result in the cancellation of the trip.
    Our MinuteMen monitor the situations closely and will intervene if necessary.""")

# =========================
# 👤 TRAVELER IDENTITY
# =========================
st.header("👤 Traveler Identity")
st.caption("Provide your personal information for timeline authorization and legal validation.")

# Split form into 2 columns for a cleaner layout
col1, col2 = st.columns(2)

# Left column: name and contact details
with col1:
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    phone = st.text_input("Phone Number", placeholder="+xx xx xxx xx xx")
    email = st.text_input("Email")

# Right column: demographics and address
with col2:
    birth_date = st.date_input("Birth Date", min_value=date(1900,1,1))
    address = st.text_input("Address")
    country = st.text_input("Country")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])

st.divider()

# =========================
# 📦 PACKAGE SELECTION
# =========================

st.header("📦 Choose Your Package")
st.caption("Each package determines your interaction level inside the selected timeline. A short description can be found on the left of the screen.")

# packages: Dict{str: Dict{str:int, str:str}}
# Maps package name to its base price (per minute in USD) and a description string
packages = {
    "Peasant Package": {
        "price": 10,
        "description": '👻 Ghost mode. Observe freely but cannot interact with people or objects.'
    },
    "Quantum Query": {
        "price": 20,
        "description": '🗣 New identity. Interact with people and objects. Languages must be purchased separately.'
    },
    "Monarch Mode": {
        "price": 50,
        "description": '👑 Full power. Bring 1 object back (max 10kg and for personal use only). All languages included. Fast travel enabled to visit multiple locations.'
    }
}

# Select a package from the dropdown (keys of the packages dictionary)
package = st.selectbox("Select Package", list(packages.keys()))

# Show the package description in the sidebar for quick reference
st.sidebar.header("📖 Package Description")
st.sidebar.info(packages[package]["description"])

# base_fee: int — per-minute price in USD for the selected package
base_fee = packages[package]["price"]

# =========================
# 👑 IDENTITY & STATUS
# =========================

# identity_multiplier: float — price multiplier based on selected fame level (default 1.0)
identity_multiplier = 1.0
# fame: int — fame level 1-5 (0 = not applicable for Peasant Package)
fame = 0

# Identity and fame selection is only shown for non-Peasant packages
if package != "Peasant Package":
    st.header("👑 Identity & Social Status")
    st.caption("Choose the level of fame and influence you wish to possess in your selected timeline.")

    fame = st.selectbox(
        "Select Fame Level (1 = Unknown Citizen, 3 = Known Figure, 5 = Very Famous Figure)",
        [1, 2, 3, 4, 5]
    )

    # Higher fame increases the price multiplicatively (each level adds +20%)
    identity_multiplier = 1 + (fame * 0.2)

st.divider()

# =========================
# ⏳ DURATION
# =========================
st.header("⏳ Duration of Travel")
st.caption("Select how long you wish to remain inside the chosen timeline. Pricing is per minute.")

# Initialize session state for minutes slider/input (default: 60 minutes)
if "minutes" not in st.session_state:
    st.session_state.minutes = 60

# update_slider: keeps the slider in sync when the number box changes
def update_slider():
    """
    Syncs the main 'minutes' slider value with the value entered in the number input box.
    This ensures that changing one input updates the other.
    """
    st.session_state.minutes = st.session_state.minutes_box

# update_box: keeps the number box in sync when the slider changes
def update_box():
    """
    Syncs the number input box value with the value selected on the 'minutes' slider.
    This ensures that sliding the bar updates the numeric display.
    """
    st.session_state.minutes_box = st.session_state.minutes

col1, col2 = st.columns(2)

# Slider and number input placed side by side for dual control
with col1:
    st.slider("Minutes in Timeline", 1, 2880, key="minutes", on_change=update_box)

with col2:
    st.number_input("Exact Minutes", 1, 2880, key="minutes_box", on_change=update_slider)

# minutes: int — final selected trip duration in minutes
minutes = st.session_state.minutes

st.divider()

# =========================
# 🌍 TIMELINE
# =========================
st.header("🌍 Choose Timeline")
st.caption("Select the historical period you want to experience. If you want to travel to a specific timeline, scroll to the bottom and select 'Personalized Timeline'.")

# Dropdown of predefined historical eras, plus a "Personalized" custom option
timeline = st.selectbox(
    "Favorite Timelines",
    [
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
        "Personalized"
    ]
)

# If user selects "Personalized", show a text input for a custom year
# Update timeline string to "Personalized (year)" for storage
if timeline == "Personalized":
    custom_year = st.text_input("Enter Custom Timeline (Year)", placeholder="e.g. 2024 or -500")
    if custom_year:
        timeline = f"Personalized ({custom_year.strip()})"
    else:
        timeline = "Personalized (Unknown)"

st.divider()

# =========================
# 📍 SPAWN COUNTRY
# =========================
st.header("📍 Spawn Country")
st.caption("Select the country where you wish to materialize in your chosen timeline. The exact location will be chosen just before your trip.")

# countries: List[str] — full list of world nations for the spawn country dropdown
countries = [
    "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda",
    "Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain",
    "Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan",
    "Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria",
    "Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada",
    "Central African Republic","Chad","Chile","China","Colombia","Comoros",
    "Congo (Congo-Brazzaville)","Costa Rica","Croatia","Cuba","Cyprus",
    "Czech Republic","Democratic Republic of the Congo","Denmark","Djibouti",
    "Dominica","Dominican Republic","Ecuador","Egypt","El Salvador",
    "Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Fiji",
    "Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece",
    "Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti",
    "Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq",
    "Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan",
    "Kenya","Kiribati","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon",
    "Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg",
    "Madagascar","Malawi","Malaysia","Maldives","Mali","Malta",
    "Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia",
    "Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique",
    "Myanmar","Namibia","Nauru","Nepal","Netherlands","New Zealand",
    "Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway",
    "Oman","Pakistan","Palau","Panama","Papua New Guinea","Paraguay",
    "Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia",
    "Rwanda","Saint Kitts and Nevis","Saint Lucia",
    "Saint Vincent and the Grenadines","Samoa","San Marino",
    "Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles",
    "Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands",
    "Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka",
    "Sudan","Suriname","Sweden","Switzerland","Syria","Tajikistan",
    "Tanzania","Thailand","Timor-Leste","Togo","Tonga",
    "Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu",
    "Uganda","Ukraine","United Arab Emirates","United Kingdom",
    "United States","Uruguay","Uzbekistan","Vanuatu","Vatican City",
    "Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"
]

# Default selection is Switzerland; falls back to index 0 if not found
spawn_country = st.selectbox(
    "Choose Country",
    sorted(countries),
    index=sorted(countries).index("Switzerland") if "Switzerland" in countries else 0
)

# =========================
# 🗣 LANGUAGES
# =========================
# language_cost: float — total cost of selected languages (only applies to Quantum Query)
language_cost = 0

# Language selection is only shown for Quantum Query and Monarch Mode packages
if package in ["Quantum Query", "Monarch Mode"]:
    st.header("🗣 Select Languages")

    # Caption differs based on whether languages cost extra or are included
    if package == "Quantum Query":
        st.caption("Purchase communication abilities for your selected era ($50 per language).")
    else:
        st.caption("Select your desired communication abilities (All languages included for free).")

    # Initialize session state for selected and custom languages
    if "selected_languages" not in st.session_state:
        st.session_state.selected_languages = []

    if "custom_language" not in st.session_state:
        st.session_state.custom_language = ""

    # add_language: function — appends the typed custom language to the selected list
    def add_language():
        """
        Adds the language from the custom text input to the session's selected_languages list.
        It trims whitespace, avoids duplicates, and then clears the input field.
        """
        lang = st.session_state.custom_language.strip()
        if lang and lang not in st.session_state.selected_languages:
            st.session_state.selected_languages.append(lang)
        st.session_state.custom_language = ""

    # base_languages: List[str] — catalog of historical and modern languages
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
    "Latvian", "Prussian", "Old Church Slavonic", "Russian", "Ukrainian",
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

    # Multiselect widget with predefined languages; pre-selected based on session state
    predefined = st.multiselect(
        "Choose Predefined Languages",
        base_languages,
        default=[lang for lang in st.session_state.selected_languages if lang in base_languages]
    )

    # Preserve custom (non-predefined) languages and merge with predefined selection
    custom_only = [lang for lang in st.session_state.selected_languages if lang not in base_languages]
    st.session_state.selected_languages = custom_only + predefined

    st.markdown("### Add Custom Language")
    st.write("You can add custom languages by typing them in the text box below and pressing Enter. Our MinuteMen will verify our data about that language and update it if needed. You will be reimboursed if the language cannot be found.")
    # Text input that calls add_language() on Enter (on_change)
    st.text_input(
        "Write language name and press Enter",
        key="custom_language",
        on_change=add_language
    )

    # Display selected languages with a delete button next to each one
    if st.session_state.selected_languages:
        st.markdown("#### Selected Languages")

        for i, lang in enumerate(st.session_state.selected_languages):
            col1, col2 = st.columns([5,1])

            # Show the language name in the left column
            with col1:
                st.write(f"• {lang}")

            # Show a delete button in the right column; removes the language on click
            with col2:
                if st.button("❌", key=f"delete_{i}"):
                    st.session_state.selected_languages.pop(i)
                    st.rerun()

    # language_cost: float — Quantum Query charges $50 per language; Monarch Mode is free
    if package == "Quantum Query":
        language_cost = 50 * len(st.session_state.selected_languages)
    else:
        language_cost = 0

else:
    # Reset language selection when switching to Peasant Package
    st.session_state.selected_languages = []

# =========================
# 🛡 ADD-ONS
# =========================
st.header("🛡 Add-ons")
st.caption("Enhance your safety and psychological protection during travel.")

# Boolean checkboxes for optional add-ons
insurance = st.checkbox("Insurance Protection ($200)")
memory_reset = st.checkbox("Memory Reset ($100)")

# Show an expandable description when each add-on is selected
with st.expander("Insurance Description"):
    st.write("Prevents permanent physical injury upon return. Pain during events cannot be prevented, we recommend travellers to be careful.")


with st.expander("Memory Reset Description"):
    st.write("Optional traumatic event erasure upon return.")

# insurance_cost, memory_cost: int — flat cost for each selected add-on (in USD)
insurance_cost = 200 if insurance else 0
memory_cost = 100 if memory_reset else 0

st.divider()

# =========================
# 💳 PAYMENT & CURRENCY
# =========================
st.header("💳 Payment Details")
st.caption("Select your preferred currency and payment method for this interdimensional transaction.")

col_pay1, col_pay2 = st.columns(2)

# Currency selection dropdown
with col_pay1:
    currency = st.selectbox(
        "Choose Currency",
        ["USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)", "CNY (¥)", "CHF (Fr)", "BTC (Bitcoin)", "ETH (Ethereum)", "CC (ChronoCredits)"]
    )

# Payment method dropdown
with col_pay2:
    payment_method = st.selectbox(
        "Payment Method",
        ["Visa", "MasterCard", "American Express", "Cash", "Twint"]
    )

st.divider()

# =========================
# 💰 PRICE CALCULATION
# =========================

# Guard: ensure selected_languages exists in session state (for Peasant Package)
if "selected_languages" not in st.session_state:
    st.session_state.selected_languages = []

# Only Quantum Query charges per language; all others get languages free or N/A
if package != "Quantum Query":
    language_cost = 0

# CURRENCY_RATES: Dict[str, float]
# Conversion multipliers relative to USD (base currency)
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

# base_price: float — duration × per-minute rate (USD)
base_price = minutes * base_fee
# fame_extra: float — additional charge from identity/fame multiplier
fame_extra = base_price * (identity_multiplier - 1)
# subtotal: float — base price + identity upgrade cost
subtotal = base_price + fame_extra
# addons_total: float — sum of all optional add-on costs
addons_total = insurance_cost + memory_cost + language_cost
# total_price: float — final USD total before currency conversion
total_price = subtotal + addons_total

# rate: float — conversion factor for the selected currency
rate = CURRENCY_RATES.get(currency, 1.0)
# converted_price: float — total in the user's selected currency
converted_price = total_price * rate
# currency_code: str — short currency code extracted from the label (e.g. "USD" from "USD ($)")
currency_code = currency.split(' ')[0]

# =========================
# 🧾 INVOICE DISPLAY
# =========================

st.header("💰 Booking Invoice")
st.caption("Transparent breakdown of your interdimensional investment.")

st.markdown("### 🧾 Cost Breakdown")

# Display travel time cost
st.write(f"⏳ Travel Time: {minutes} min × ${base_fee} = **${base_price:,.2f}**")

# Display identity upgrade cost if fame level is selected
if fame > 0:
    st.write(f"👑 Identity Upgrade = **+${fame_extra:,.2f}**")

# Display selected languages with individual costs
if package in ["Quantum Query", "Monarch Mode"] and st.session_state.selected_languages:
    st.write("🗣 Languages:")
    for lang in st.session_state.selected_languages:
        if package == "Quantum Query":
            st.write(f"   • {lang} - **$50.00**")
        else:
            st.write(f"   • {lang} - **Included**")

# Display insurance cost if selected
if insurance:
    st.write(f"🛡 Insurance Protection = **+${insurance_cost:,.2f}**")

# Display memory reset cost if selected
if memory_reset:
    st.write(f"🧠 Memory Reset = **+${memory_cost:,.2f}**")

st.markdown("---")

st.markdown(f"**Subtotal (Travel + Identity):** ${subtotal:,.2f}")
st.markdown(f"**Add-ons Total:** ${addons_total:,.2f}")

st.markdown("## 💵 TOTAL PRICE")
st.markdown(f"# ${total_price:,.2f}")

st.info(f"💳 Final amount in your selected currency: **{converted_price:,.2f} {currency_code}**")

st.divider()

# =========================
# 🚀 CONFIRM AND INSERTION INTO DATABASE
# =========================

# When the Confirm Booking button is pressed, validate and insert all records
if st.button("Confirm Booking"):

    # 1. Validation: both first and last name are required
    if not first_name or not last_name:
        st.error("Please enter traveler identity.")

    else:
        # 2. Open a database connection using the configured backend
        conn = get_connection()
        cursor = conn.cursor()

        # -------------------------
        # 3. INSERT CUSTOMER
        # -------------------------
        # Use email as the unique identifier to detect returning customers
        cursor.execute(
            f'SELECT customer_id FROM "Customer" WHERE email={PL}',
            (email,)
        )

        result = cursor.fetchone()

        # If the customer already exists, reuse their existing ID
        if result:
            customer_id = result[0]

        # If this is a new customer, insert their record and retrieve the new ID
        else:
            customer_query = f"""
            INSERT INTO "Customer"
            (first_name, last_name, phone_num, address, birthdate, email, sex)
            VALUES ({PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL})
            """
            if os.getenv("SUPABASE_DB_URL"):
                # RETURNING customer_id fetches the new ID immediately in PostgreSQL
                customer_query += " RETURNING customer_id"

            cursor.execute(customer_query, (
                first_name,
                last_name,
                phone,
                address,
                birth_date,
                email,
                sex
            ))

            # Retrieve the newly generated primary key
            if os.getenv("SUPABASE_DB_URL"):
                customer_id = cursor.fetchone()[0]
            else:
                # SQLite: use lastrowid to get the last inserted ID
                customer_id = cursor.lastrowid


        # -------------------------
        # 4. INSERT TIMELINE
        # -------------------------
        # Every trip gets its own Timeline entry (era label + spawn country as map)
        timeline_query = f"""
        INSERT INTO "Timeline" (timeline_year, map)
        VALUES ({PL}, {PL})
        """
        if os.getenv("SUPABASE_DB_URL"):
            timeline_query += " RETURNING timeline_id"

        cursor.execute(timeline_query, (
            timeline,
            spawn_country
        ))

        if os.getenv("SUPABASE_DB_URL"):
            timeline_id = cursor.fetchone()[0]
        else:
            timeline_id = cursor.lastrowid


        # -------------------------
        # 5. GET PACKAGE ID
        # -------------------------
        # Look up the integer primary key for the selected package name
        cursor.execute(f'SELECT package_id FROM "Packages" WHERE description={PL}', (package,))
        package_id_result = cursor.fetchone()
        # package_id: int or None — the matching package's primary key
        package_id = package_id_result[0] if package_id_result else None

        # -------------------------
        # 6. ASSIGN RANDOM MINUTEMAN
        # -------------------------
        # Fetch all available agents from the MinuteMen table
        cursor.execute('SELECT agent_id, agent_name, badge_number FROM "MinuteMen"')
        all_agents = cursor.fetchall()

        # Randomly select one agent to monitor this trip
        assigned_agent = random.choice(all_agents)
        # Unpack: agent_id (int), agent_name (str), agent_badge (str)
        agent_id = assigned_agent[0]
        agent_name = assigned_agent[1]
        agent_badge = assigned_agent[2]

        # -------------------------
        # 7. PROCESS LANGUAGES
        # -------------------------
        # We store languages as a comma-separated string of language IDs
        # language_ids: List[str] — collects the integer ID for each selected language
        language_ids = []
        for lang in st.session_state.selected_languages:
            # Insert the language if it doesn't exist yet (custom languages may be new)
            if os.getenv("SUPABASE_DB_URL"):
                cursor.execute(
                    f'INSERT INTO "Languages" (language_name) VALUES ({PL}) ON CONFLICT (language_name) DO NOTHING',
                    (lang,)
                )
            else:
                cursor.execute(
                    f'INSERT OR IGNORE INTO "Languages" (language_name) VALUES ({PL})',
                    (lang,)
                )
            # Retrieve the language's primary key ID
            cursor.execute(
                f'SELECT language_id FROM "Languages" WHERE language_name={PL}',
                (lang,)
            )

            # Append the string ID to the list for joining later
            language_ids.append(str(cursor.fetchone()[0]))

        # Join all language IDs into a single comma-separated string (e.g. "1,5,12")
        booking_languages_str = ",".join(language_ids)

        # -------------------------
        # 8. INSERT BOOKING
        # -------------------------
        # Add RETURNING clause for PostgreSQL to get the new booking_id immediately
        booking_query = f"""
        INSERT INTO "Booking"
        (customer_id, package_id, timeline_id, spawn_country, minutes,
         insurance, memory_reset, total_price, booking_languages, fame_level, agent_id)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL}, {PL})
        """
        if os.getenv("SUPABASE_DB_URL"):
            booking_query += " RETURNING booking_id"

        cursor.execute(booking_query, (
            customer_id,
            package_id,
            timeline_id,
            spawn_country,
            minutes,
            insurance,
            memory_reset,
            total_price,
            booking_languages_str,
            fame,
            agent_id
        ))

        # Retrieve the new booking_id from the database
        if os.getenv("SUPABASE_DB_URL"):
            booking_id = cursor.fetchone()[0]
        else:
            booking_id = cursor.lastrowid

        # -------------------------
        # 8b. INSERT IDENTITY & CONFIRM
        # -------------------------
        # Only non-Peasant travelers get a fake alias identity
        if package != "Peasant Package":
            # Generate a realistic fake name matching the traveler's sex using Faker
            if sex == "Male":
                random_first = fake.first_name_male()
            elif sex == "Female":
                random_first = fake.first_name_female()
            else:
                random_first = fake.first_name_nonbinary()

            random_last = fake.last_name()

            cursor.execute(f"""
        INSERT INTO "Identities" (first_name, last_name, sex, fame_level, booking_id)
        VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
        """, (random_first, random_last, sex, fame, booking_id))

            # -------------------------
            # 9. INSERT PAYMENT
            # -------------------------
            # Link the converted price and payment method to this booking
            cursor.execute(f"""
            INSERT INTO "Payments" (amount, currency, method, customer_id, booking_id)
            VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
            """, (converted_price, currency_code, payment_method, customer_id, booking_id))

            # Save all changes and close the connection
            conn.commit()
            conn.close()

            st.success(f"🚀 Booking Confirmed! Your generated timeline alias is **{random_first} {random_last}**. {agent_name} (Badge {agent_badge}) will monitor your travel closely. Do not violate protocol.")

        else:
            # -------------------------
            # 9. INSERT PAYMENT (Peasant Package)
            # -------------------------
            # Peasant travelers have no identity — payment still recorded
            cursor.execute(f"""
            INSERT INTO "Payments" (amount, currency, method, customer_id, booking_id)
            VALUES ({PL}, {PL}, {PL}, {PL}, {PL})
            """, (converted_price, currency_code, payment_method, customer_id, booking_id))

            # Save all changes and close the connection
            conn.commit()
            conn.close()
            st.success(f"🚀 Booking Confirmed for {first_name} {last_name}! {agent_name} (Badge {agent_badge}) has been assigned to guard your spectral observation.")

# =========================
# 📊 ANALYTICS TAB
# =========================

# All analytics charts are rendered inside the analytics tab context
with tab_analytics:
    st.header("📊 Time Travel Analytics Dashboard")
    st.caption("Live insights from the booking database.")

    # Wrap in try/except to gracefully handle database connection failures
    try:
        # Open a separate analytics connection (does not interfere with booking flow)
        conn_a = get_connection()

        # --- KPI (Key Performance Indicator) Row ---
        # Display 4 metrics side by side in column layout
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        # Use pd.read_sql to query each metric directly from the database
        kpi1.metric("Total Bookings",   pd.read_sql('SELECT COUNT(*) FROM "Booking"', conn_a).iloc[0, 0])
        query_revenue = 'SELECT COALESCE(SUM(total_price),0) FROM "Booking"'
        kpi2.metric("Total Revenue ($)", f"{pd.read_sql(query_revenue, conn_a).iloc[0,0]:,.0f}")
        kpi3.metric("Unique Travelers",  pd.read_sql('SELECT COUNT(*) FROM "Customer"', conn_a).iloc[0, 0])
        kpi4.metric("Avg Trip (min)",    round(pd.read_sql('SELECT COALESCE(AVG(minutes),0) FROM "Booking"', conn_a).iloc[0, 0], 1))

        st.divider()

        # --- Chart 1: Professional Timeline (Full Width) ---
        st.subheader("🌍 Chronological Timeline of Trips")
        st.caption("A log-scaled view of trips throughout history. Hover to see exact years.")

        # Fetch trips grouped by era label
        df_tl_raw = pd.read_sql("""
            SELECT t.timeline_year, COUNT(b.booking_id) AS trips
            FROM "Booking" b
            JOIN "Timeline" t ON b.timeline_id = t.timeline_id
            GROUP BY t.timeline_year
        """, conn_a)

        # Helper function: extracts the numeric year from strings like "Roman Empire (100)"
        # Returns int (0 if parsing fails or no parentheses found)
        def extract_year(val):
            try:
                # Look for content inside the trailing parentheses
                if '(' in val:
                    year_str = val.split('(')[-1].split(')')[0].replace(',', '')
                    return int(year_str)
                return 0
            except:
                return 0

        # Apply the extractor to create a numeric year column for sorting
        df_tl_raw['YearNumeric'] = df_tl_raw['timeline_year'].apply(extract_year)

        # Sort by year so the line chart connects eras chronologically
        df_tl_raw = df_tl_raw.sort_values('YearNumeric')

        # Transform to "Years Before Present" for a log scale
        # (log scale requires positive values, and modern years are near-zero)
        present_year = 2026
        df_tl_raw['YearsAgo'] = (present_year - df_tl_raw['YearNumeric']) + 1

        # Create a line chart with markers using Plotly Express
        fig_tl = px.line(
            df_tl_raw,
            x='YearsAgo',
            y='trips',
            markers=True,
            hover_name='timeline_year',
            color_discrete_sequence=["#00D4FF"],
            labels={'YearsAgo': 'Years Before Present (Log Scale)', 'trips': 'Number of Bookings'}
        )

        # Use a log x-axis reversed so ancient eras appear on the left
        fig_tl.update_xaxes(type="log", autorange="reversed")
        fig_tl.update_layout(height=450)

        st.plotly_chart(fig_tl, use_container_width=True)
        st.info("💡 Note: Timeline uses a logarithmic scale to display everything from the Dinosaurs Era to today accurately.")

        st.divider()

        col_left, col_right = st.columns(2)

        # --- Chart 2: Revenue by Package ---
        with col_right:
            st.subheader("💰 Revenue by Package")
            # Join Booking and Packages to group revenue and trip counts by package name
            df_pkg = pd.read_sql("""
                SELECT p.description AS package,
                       COUNT(b.booking_id) AS trips,
                       SUM(b.total_price) AS revenue
                FROM "Booking" b
                JOIN "Packages" p ON b.package_id = p.package_id
                GROUP BY p.description
            """, conn_a)
            st.bar_chart(df_pkg.set_index("package")["revenue"], color="#FF4B4B")

        st.divider()

        col_left2, col_right2 = st.columns(2)

        # --- Chart 3: Gender Split ---
        with col_left2:
            st.subheader("👤 Traveler Gender Split")
            # Count customers by sex category
            df_sex = pd.read_sql("""
                SELECT sex AS sex_col, COUNT(*) AS count_val
                FROM "Customer"
                GROUP BY sex
            """, conn_a)
            st.bar_chart(df_sex.set_index("sex_col"), color="#00FFAA")

        # --- Chart 4: MinuteMen Deployments ---
        with col_right2:
            st.subheader("🕵️ MinuteMen Deployments")
            # Count bookings per agent to show deployment frequency
            df_agents = pd.read_sql("""
                SELECT m.agent_name AS agent_name_col, COUNT(b.booking_id) AS assignments
                FROM "Booking" b
                JOIN "MinuteMen" m ON b.agent_id = m.agent_id
                GROUP BY m.agent_name
                ORDER BY assignments DESC
            """, conn_a)
            st.bar_chart(df_agents.set_index("agent_name_col"), color="#FFD700")

        st.divider()

        col_left3, col_right3 = st.columns(2)

        # --- Chart 5: Add-ons Distribution ---
        with col_left3:
            st.subheader("🛡 Add-ons Combinations")
            # Count bookings for each combination of insurance and memory_reset
            # T_VAL/F_VAL handle boolean literals for the active database type
            none_ct   = pd.read_sql(f'SELECT COUNT(*) FROM "Booking" WHERE insurance = {F_VAL} AND memory_reset = {F_VAL}', conn_a).iloc[0, 0]
            ins_only  = pd.read_sql(f'SELECT COUNT(*) FROM "Booking" WHERE insurance = {T_VAL} AND memory_reset = {F_VAL}', conn_a).iloc[0, 0]
            mem_only  = pd.read_sql(f'SELECT COUNT(*) FROM "Booking" WHERE insurance = {F_VAL} AND memory_reset = {T_VAL}', conn_a).iloc[0, 0]
            both_ct   = pd.read_sql(f'SELECT COUNT(*) FROM "Booking" WHERE insurance = {T_VAL} AND memory_reset = {T_VAL}', conn_a).iloc[0, 0]
            # Construct a DataFrame from the four counts for charting
            df_addons = pd.DataFrame({
                "Combination": ["None", "Insurance Only", "Memory Reset Only", "Both"],
                "Bookings": [none_ct, ins_only, mem_only, both_ct]
            })
            st.bar_chart(df_addons.set_index("Combination"), color="#BD00FF")

        # --- Chart 6: Fame Level Distribution ---
        with col_right3:
            st.subheader("👑 Fame Level Distribution")
            # Count non-zero fame bookings grouped by fame level (1-5)
            df_fame = pd.read_sql("""
                SELECT fame_level AS fame_level_col, COUNT(*) AS bookings
                FROM "Booking"
                WHERE fame_level > 0
                GROUP BY fame_level
                ORDER BY fame_level
            """, conn_a)
            if not df_fame.empty:
                st.bar_chart(df_fame.set_index("fame_level_col"), color="#FF8A00")
            else:
                st.info("No fame data yet.")

        st.divider()

        # --- Chart 7: Violation Distribution ---
        st.subheader("⚖️ Crimes & Violations")
        st.caption("Distribution of reported violations across all trips.")

        # Join Trip_Violations and Violations to count violations by crime type
        df_violations = pd.read_sql("""
            SELECT v.crime AS crime, COUNT(tv.trip_violation_id) AS violation_count
            FROM "Trip_Violations" tv
            JOIN "Violations" v ON tv.violation_id = v.violation_id
            GROUP BY v.crime
            ORDER BY violation_count DESC
        """, conn_a)

        if not df_violations.empty:
            st.bar_chart(df_violations.set_index("crime"), color="#33FF57")
        else:
            st.info("No violations recorded. The Timeline is currently stable.")

        # Close the analytics connection after all charts are rendered
        conn_a.close()

    except Exception as e:
        st.error(f"Analytics error: {e}")
