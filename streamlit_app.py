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
# 📍 SPAWN COUNTRY
# =========================
st.header("📍 Spawn Country")
st.caption("Select the country where you wish to materialize in your chosen timeline.")

# Full country list (ISO standard list)
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

spawn_country = st.selectbox(
    "Choose Country",
    sorted(countries),
    index=sorted(countries).index("Switzerland") if "Switzerland" in countries else 0
)
# =========================
# 🗣 LANGUAGES
# =========================
language_cost = 0

if package == "Quantum Query":
    st.header("🗣 Select Languages")
    st.caption("Purchase communication abilities for your selected era ($50 per language).")

    # Initialize session state safely
    if "selected_languages" not in st.session_state:
        st.session_state.selected_languages = []

    if "custom_language" not in st.session_state:
        st.session_state.custom_language = ""

    # Function to add custom language safely
    def add_language():
        lang = st.session_state.custom_language.strip()
        if lang and lang not in st.session_state.selected_languages:
            st.session_state.selected_languages.append(lang)
        st.session_state.custom_language = ""  # Safe reset inside callback

    # Predefined languages
    base_languages = ["Latin", "Ancient Greek", "Old French", "Germanic"]

    predefined = st.multiselect(
        "Choose Predefined Languages",
        base_languages,
        default=[lang for lang in st.session_state.selected_languages if lang in base_languages]
    )

    # Keep only custom ones + selected predefined
    custom_only = [lang for lang in st.session_state.selected_languages if lang not in base_languages]
    st.session_state.selected_languages = custom_only + predefined

    st.markdown("### Add Custom Language")

    st.text_input(
        "Write language name",
        key="custom_language",
        on_change=add_language
    )

    # Display selected languages nicely
    if st.session_state.selected_languages:
        st.markdown("#### Selected Languages:")
        for lang in st.session_state.selected_languages:
            st.write(f"• {lang}")

    language_cost = 50 * len(st.session_state.selected_languages)

else:
    # Reset safely if package changes
    if "selected_languages" in st.session_state:
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

# --- Safe defaults ---
if "selected_languages" not in st.session_state:
    st.session_state.selected_languages = []

if package != "Quantum Query":
    language_cost = 0

# --- Calculations ---
base_price = minutes * base_fee
fame_extra = base_price * (identity_multiplier - 1)
subtotal = base_price + fame_extra
addons_total = insurance_cost + memory_cost + language_cost
total_price = subtotal + addons_total

# =========================
# 🧾 INVOICE DISPLAY
# =========================

st.header("💰 Booking Invoice")
st.caption("Transparent breakdown of your interdimensional investment.")

st.markdown("### 🧾 Cost Breakdown")

st.write(f"⏳ Travel Time: {minutes} min × ${base_fee} = **${base_price:,.2f}**")

if fame > 0:
    st.write(f"👑 Identity Upgrade = **+${fame_extra:,.2f}**")

# Languages (safe version)
if package == "Quantum Query" and st.session_state.selected_languages:
    st.write("🗣 Languages:")
    for lang in st.session_state.selected_languages:
        st.write(f"   • {lang} - **$50.00**")

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
