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
    phone = st.text_input("Phone number")

with col2:
    birth_date = st.date_input("Birth Date", min_value=date(1900,1,1))
    address = st.text_input("Address")
    country = st.text_input("Country")

st.divider()

# =========================
# 📦 PACKAGE SELECTION (NOW MAIN PAGE)
# =========================
st.header("📦 Choose Your Package")

packages = {
    "Peasant Package": {
        "price": 10,
        "description": '👻 Ghost mode. You like safaris and don\'t know how to interact with people? '
                       'This is the right package for you. With the "Peasant Package", '
                       "you'll be able to discover a new timeline without holding a conversation!"
    },
    "Quantum Query": {
        "price": 20,
        "description": '🗣 Interact with people and objects. Are you curious about social norms '
                       'and want to be included? The "Quantum Query" is the perfect fit. '
                       "Our MinuteMen will help you choose the right languages!"
    },
    "Monarch Mode": {
        "price": 50,
        "description": '👑 Full power. Bring objects back. All languages included. '
                       "Fast travel enabled. Better than the cold side of a pillow in summer."
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
# 👑 IDENTITY & STATUS
# =========================
identity_multiplier = 1.0
fame = 0

if package != "Peasant Package":
    st.header("👑 Identity & Social Status")
    st.caption("Choose the level of fame and influence you wish to possess in your selected timeline.")

    fame = st.selectbox(
        "Select Fame Level (1 = Unknown Citizen, 5 = Legendary Figure)",
        [1, 2, 3, 4, 5]
    )

    identity_multiplier = 1 + (fame * 0.2)
# =========================
# 🗣 LANGUAGES
# =========================
language_cost = 0
selected_languages = []

if package == "Quantum Query":
    st.header("🗣 Select Languages")
    st.caption("As you will interact with people, you may choose 1 or more languages.")

    languages = st.multiselect(
        "Choose Languages ($50 each)",
        ["Latin", "Ancient Greek", "Old French", "Germanic", "Other..."]
    )

    if "Other..." in languages:
        custom_language = st.text_input("Enter Custom Language")
        if custom_language:
            selected_languages.append(custom_language)

    selected_languages += [lang for lang in languages if lang != "Other..."]

    language_cost = 50 * len(selected_languages)

# =========================
# 🛡 ADD-ONS
# =========================
st.header("🛡 Add-ons")
st.caption("Insurance covers physical injury protection : No physical injury at the comeback from the trip. Note: Pain during the event cannot be prevented. Memory reset covers optional traumatic event erasure. ")
insurance = st.checkbox("Insurance Protection ($200)")

memory_reset = st.checkbox("Memory Reset ($100)")


insurance_cost = 200 if insurance else 0
memory_cost = 100 if memory_reset else 0

# =========================
# 💰 PRICE CALCULATION
# =========================
base_price = minutes * base_fee
fame_extra = base_price * (identity_multiplier - 1)
premium_price = base_price + fame_extra

total_price = premium_price + insurance_cost + memory_cost + language_cost

st.header("💰 Booking Invoice")

st.markdown("### 🧾 Cost Breakdown")

st.write(f"⏳ Travel Time: {minutes} min × ${base_fee} = **${base_price:,.2f}**")

if fame > 0:
    st.write(f"👑 Fame Multiplier Adjustment = **+${fame_extra:,.2f}**")

if language_cost > 0:
    st.write(f"🗣 Languages ({len(selected_languages)} × $50) = **+${language_cost:,.2f}**")

if insurance:
    st.write(f"🛡 Insurance Protection = **+${insurance_cost:,.2f}**")

if memory_reset:
    st.write(f"🧠 Memory Reset = **+${memory_cost:,.2f}**")

st.markdown("---")

st.markdown(f"# 💵 TOTAL = ${total_price:,.2f}")

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
