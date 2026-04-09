# ⏳ LevarT Time Travel - The Future of Tourism

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-6jipuxwzfe.streamlit.app/)

Welcome to **LevarT**, the premier interdimensional travel agency. This application provides a full-stack platform for booking historical travel across timelines, ensuring safety, legality, and the complete absence of butterfly effects through advanced temporal duplication and pruning.

## 🚀 Key Features

### 🛠️ Core Booking Engine
*   **Traveler Identity Management:** Secure registration of personal data for timeline authorization.
*   **Tiered Service Packages:**
    *   **Peasant Package:** Ghost mode observation with zero interaction.
    *   **Quantum Query:** Full interaction with new identities and language modules.
    *   **Monarch Mode:** Ultimate power, fast travel, and object retrieval capabilities.
*   **Dynamic Customization:** Choose from predefined historical eras (Ancient Egypt, Viking Age, etc.) or specify a "Personalized Timeline."
*   **Language Acquisition:** Real-time selection of ancient and modern languages (Sumerian, Gothic, Old Norse, etc.).
*   **Add-ons:** Optional "Insurance Protection" (physical safety) and "Memory Reset" (traumatic event erasure).

### 💳 Financial System
*   **Multi-Currency Engine:** Live price conversion across USD, EUR, GBP, JPY, CHF, and even cryptocurrencies like BTC and ETH.
*   **Dynamic Pricing:** Calculations based on duration, package tier, fame multipliers, and selected add-ons.

### 📊 Professional Analytics Dashboard
*   **Real-time KPIs:** Monitor total bookings, revenue, unique travelers, and average trip durations.
*   **Data Visualization:** Interactive insights into timeline trends and financial performance powered by Plotly.

### 🛡️ Safety & Protocol
*   **MinuteMen Monitoring:** Every booking is assigned a dedicated agent (MinuteMen) to guard the traveler and ensure protocol compliance.
*   **Alias Generation:** Automatic generation of timeline-appropriate identities for Quantum and Monarch travelers.

## 🛠️ Tech Stack
*   **Frontend:** [Streamlit](https://streamlit.io/) (Python)
*   **Database:** 
    *   **Local:** SQLite
    *   **Production:** PostgreSQL (hosted via **Supabase**)
*   **Data Science:** Pandas, Plotly, Faker
*   **Environment:** Python 3.9+, `python-dotenv`, `psycopg2`

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Al-hess/time_travel_01.git
cd time_travel_01
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory to enable Supabase/PostgreSQL connectivity. If not present, the app will automatically fall back to local SQLite (`time_travel.db`).

```env
SUPABASE_DB_URL=your_postgresql_connection_string
```

### 4. Run the Application
```bash
streamlit run streamlit_app.py
```

## 📜 Legal Note
Breach of temporal violations result in immediate cancellation and potential intervention by MinuteMen agents. Travel safely!

## 📄 License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
