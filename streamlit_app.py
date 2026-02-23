import streamlit as st
from datetime import date

st.set_page_config(page_title="LevarT EmiT - Time Travel", page_icon="⏳", layout="wide")

st.title("⏳ LevarT EmiT - Time Travel")
st.write("The Future of Tourism.")

# =========================
# 👤 TRAVELER IDENTITY
# =========================
st.header("👤 Traveler Identity")

col1, col2 = st.columns(2)

with col1:
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")

with col2:
    birth_date = st.date_input("Birth Date", min_value=date(1900,1,1))

st.divider()

# =========================
# 📦 PACKAGE SELECTION (NOW MAIN PAGE)
# =========================
st.header("📦 Choose Your Package")

packages = {
    "Peasant Package": {
        "price": 5,
        "description": "👻 Ghost mode. Observe freely but cannot interact."
    },
    "Quantum Query": {
        "price": 15,
        "description": "🗣 Interact with people and objects. Languages sold separately."
    },
    "Monarch Mode": {
        "price": 50,
        "description": "👑 Full power. Bring objects back. All languages included. Fast travel enabled."
    }
}

package = st.selectbox("Select Package", list(packages.keys()))

# Sidebar description (dynamic)
st.sidebar.header("📖 Package Description")
st.sidebar.info(packages[package]["description"])

base_fee = packages[package]["price"]

st.divider()

# =========================
# ⏳ MINUTES INPUT (SYNCED)
# =========================
st.header("⏳ Duration of Travel")

# Initialize session state
if "minutes" not in st.session_state:
    st.session_state.minutes = 60

def update_slider():
    st.session_state.minutes = st.session_state.minutes_box

def update_box():
    st.session_state.minutes_box = st.session_state.minutes

col1, col2 = st.columns(2)

with col1:
    st.slider(
        "Minutes in Timeline",
        1,
        2880,
        key="minutes",
        on_change=update_box
    )

with col2:
    st.number_input(
        "Exact Minutes",
        1,
        2880,
        key="minutes_box",
        on_change=update_slider
    )

minutes = st.session_state.minutes

st.divider()

# =========================
# 🌍 TIMELINE
# =========================
st.header("🌍 Choose Timeline")

timeline = st.selectbox(
    "Favorite Timelines",
    [
        "Dinosaurs Era (-65'000'000)",
        "Ancient Greece (-1000)",
        "Ancient Rome (-50)",
        "Medieval Europe (1350)",
        "Industrial Revolution (1800)",
        "WW2 (1940)",
        "Personalized"
    ]
)

if timeline == "Personalized":
    timeline = st.text_input("Enter Custom Timeline (Year)")

st.divider()

# =========================
# 👑 FAME LEVEL
# =========================
identity_multiplier = 1.0
fame = 0

if package != "Peasant Package":
    st.header("👑 Fame & Status")
    fame = st.selectbox("Select Identity Fame Level", [1,2,3,4,5])
    identity_multiplier = 1 + (fame * 0.2)

# =========================
# 🗣 LANGUAGES
# =========================
language_cost = 0

if package == "Quantum Query":
    st.header("🗣 Select Languages")
    languages = st.multiselect(
        "Choose Languages ($50 each)",
        ["Latin", "Ancient Greek", "Old French", "Germanic", "Martian Basic"]
    )
    language_cost = 50 * len(languages)

# =========================
# 🛡 ADD-ONS
# =========================
st.header("🛡 Add-ons")

insurance = st.checkbox("Insurance Protection ($200)")
memory_reset = st.checkbox("Memory Reset ($100)")

insurance_cost = 200 if insurance else 0
memory_cost = 100 if memory_reset else 0

st.divider()

# =========================
# 💰 PRICE CALCULATION
# =========================
base_price = minutes * base_fee
premium_price = base_price * identity_multiplier

total_price = premium_price + insurance_cost + memory_cost + language_cost

st.header("💰 Price Breakdown")

st.write(
    f"{minutes} min × ${base_fee}"
    f"{' × Fame Multiplier' if fame > 0 else ''}"
    f" + ${insurance_cost} (Insurance)"
    f" + ${memory_cost} (Memory Reset)"
    f" + ${language_cost} (Languages)"
)

st.success(f"TOTAL = ${total_price:,.2f}")

# =========================
# 🚀 CONFIRM
# =========================
if st.button("Confirm Booking"):
    if not first_name or not last_name:
        st.error("Please enter traveler identity.")
    else:
        st.success(
            f"🚀 Booking Confirmed for {first_name} {last_name}!\n\n"
            "Our MinuteMen will monitor your travel."
        )
