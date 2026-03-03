import streamlit as st
from datetime import date

st.set_page_config(page_title="LevarT EmiT - Time Travel", page_icon="⏳", layout="wide")

st.title("⏳ LevarT EmiT - Time Travel")
st.write("### The Future of Tourism.")
st.caption("Travel across timelines safely, legally, and without butterfly effects.")

st.divider()

# =========================
# 👤 TRAVELER IDENTITY
# =========================
st.header("👤 Traveler Identity")
st.caption("Provide your personal information for timeline authorization and legal validation.")

col1, col2 = st.columns(2)

with col1:
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    phone = st.text_input("Phone Number")

with col2:
    birth_date = st.date_input("Birth Date", min_value=date(1900,1,1))
    address = st.text_input("Address")
    country = st.text_input("Country")

st.divider()

# =========================
# 📦 PACKAGE SELECTION
# =========================
st.header("📦 Choose Your Package")
st.caption("Each package determines your interaction level inside the selected timeline.")

packages = {
    "Peasant Package": {
        "price": 10,
        "description": '👻 Ghost mode. Observe freely but cannot interact with people or objects.'
    },
    "Quantum Query": {
        "price": 20,
        "description": '🗣 Interact with people and objects. Languages must be purchased separately.'
    },
    "Monarch Mode": {
        "price": 50,
        "description": '👑 Full power. Bring objects back. All languages included. Fast travel enabled.'
    }
}

package = st.selectbox("Select Package", list(packages.keys()))

st.sidebar.header("📖 Package Description")
st.sidebar.info(packages[package]["description"])

base_fee = packages[package]["price"]

# =========================
# 👑 IDENTITY & STATUS (Moved Here)
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

st.divider()

# =========================
# ⏳ DURATION
# =========================
st.header("⏳ Duration of Travel")
st.caption("Select how long you wish to remain inside the chosen timeline. Pricing is per minute.")

if "minutes" not in st.session_state:
    st.session_state.minutes = 60

def update_slider():
    st.session_state.minutes = st.session_state.minutes_box

def update_box():
    st.session_state.minutes_box = st.session_state.minutes

col1, col2 = st.columns(2)

with col1:
    st.slider("Minutes in Timeline", 1, 2880, key="minutes", on_change=update_box)

with col2:
    st.number_input("Exact Minutes", 1, 2880, key="minutes_box", on_change=update_slider)

minutes = st.session_state.minutes

st.divider()

# =========================
# 🌍 TIMELINE
# =========================
st.header("🌍 Choose Timeline")
st.caption("Select the historical period you want to experience. No butterfly effects included.")

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
# 🗣 LANGUAGES
# =========================
language_cost = 0

if package == "Quantum Query":
    st.header("🗣 Select Languages")
    st.caption("Purchase communication abilities for your selected era ($50 per language).")

    # Initialize session state
    if "selected_languages" not in st.session_state:
        st.session_state.selected_languages = []

    if "custom_input" not in st.session_state:
        st.session_state.custom_input = ""

    # Base languages
    base_languages = ["Latin", "Ancient Greek", "Old French", "Germanic"]

    # Select predefined languages
    predefined = st.multiselect(
        "Choose Predefined Languages",
        base_languages,
        default=[lang for lang in st.session_state.selected_languages if lang in base_languages]
    )

    # Update session state with predefined selections
    st.session_state.selected_languages = [
        lang for lang in st.session_state.selected_languages if lang not in base_languages
    ] + predefined

    st.markdown("### Add Custom Language")

    col1, col2 = st.columns([3,1])

    with col1:
        custom_language = st.text_input(
            "Write language name",
            key="custom_input"
        )

    with col2:
        if st.button("Add"):
            if custom_language and custom_language not in st.session_state.selected_languages:
                st.session_state.selected_languages.append(custom_language)
                st.session_state.custom_input = ""

    # Remove duplicates safely
    st.session_state.selected_languages = list(dict.fromkeys(st.session_state.selected_languages))

    language_cost = 50 * len(st.session_state.selected_languages)

else:
    # Reset languages if user switches package
    st.session_state.selected_languages = []
# =========================
# 🛡 ADD-ONS
# =========================
st.header("🛡 Add-ons")
st.caption("Enhance your safety and psychological protection during travel.")

insurance = st.checkbox("Insurance Protection ($200)")
memory_reset = st.checkbox("Memory Reset ($100)")

if insurance:
    with st.expander("Insurance Description"):
        st.write("Prevents permanent physical injury upon return. Pain during events cannot be prevented.")

if memory_reset:
    with st.expander("Memory Reset Description"):
        st.write("Optional traumatic event erasure upon return.")

insurance_cost = 200 if insurance else 0
memory_cost = 100 if memory_reset else 0

st.divider()

# =========================
# 💰 PRICE CALCULATION
# =========================
base_price = minutes * base_fee
fame_extra = base_price * (identity_multiplier - 1)
subtotal = base_price + fame_extra
addons_total = insurance_cost + memory_cost + language_cost
total_price = subtotal + addons_total

st.header("💰 Booking Invoice")
st.caption("Transparent breakdown of your interdimensional investment.")

st.markdown("### 🧾 Cost Breakdown")

st.write(f"⏳ Travel Time: {minutes} min × ${base_fee} = **${base_price:,.2f}**")

if fame > 0:
    st.write(f"👑 Identity Upgrade = **+${fame_extra:,.2f}**")

if language_cost > 0:
    st.write(f"🗣 Languages ({len(selected_languages)} × $50) = **+${language_cost:,.2f}**")

if insurance:
    st.write(f"🛡 Insurance Protection = **+${insurance_cost:,.2f}**")

if memory_reset:
    st.write(f"🧠 Memory Reset = **+${memory_cost:,.2f}**")

st.markdown("---")

st.markdown(f"**Subtotal (Travel + Identity):** ${subtotal:,.2f}")
st.markdown(f"**Add-ons Total:** ${addons_total:,.2f}")

st.markdown("## 💵 TOTAL PRICE")
st.markdown(f"# ${total_price:,.2f}")

st.divider()

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
