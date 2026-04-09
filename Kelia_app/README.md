# 🌸 Simp App - Personal Cooking & Activity Hub

A beautiful, mobile-friendly personal management platform designed for tracking recipes, activities, movies, and more. Built with Streamlit and optimized for meaningful daily use.

## 🚀 Key Features

### 👨‍🍳 Recipe Management
*   **Full CRUD Support:** Create, edit, and manage your favorite recipes with ease.
*   **Rich Recipe Details:** Store servings, prep/cook time, author names, and custom notes.
*   **Photo Support:** Upload and store final dish images directly in the database.
*   **Structured Lists:** Dedicated tables for ingredients and step-by-step instructions.
*   **Dynamic Categories:** Organize your kitchen with built-in categories (Pasta, Salads, Street Food, etc.) or create your own on the fly.

### 🏃 Activity & Lifestyle Tracker
*   **Activity Hub:** Categorized activity management (Outdoor, Sport, Creative, Games, etc.).
*   **Incentive Tracking:** Track costs, durations, and "sport value" for physical activities.
*   **Favorites:** Keep your most-loved recipes and activities pinned for quick access.

### 🍿 Entertainment & Utilities
*   **Movie Watchlist:** Track films you want to see, categorized by genre with a "watched" status.
*   **Day Counters:** Internal tracking system for monitoring lifestyle streaks or specific events.

### 🛠️ Technical Excellence
*   **Multi-Backend Support:** Seamlessly switches between local **SQLite** and cloud **PostgreSQL (Supabase)** based on your configuration.
*   **Premium UI:** Custom CSS design featuring a "Simp" aesthetic (Playfair Display typography, soft coral/cream palette).
*   **PWA Ready:** Designed to behave like a native app when saved to a mobile home screen.

## 🛠️ Tech Stack
*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Database:** SQLite / PostgreSQL
*   **Libraries:** `Pandas`, `Pillow` (PIL), `psycopg2`
*   **UI/UX:** Custom HTML/CSS Injection

## ⚙️ Setup & Deployment

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
The app uses **SQLite** by default. To enable persistent cloud storage via **Supabase**, add the following to your `.streamlit/secrets.toml`:

```toml
[supabase_cooking]
url = "your_postgresql_connection_string"
```

### 3. Run Locally
```bash
streamlit run Kelia-cook.py
```

## 📱 Mobile Usage
For the best experience on iOS or Android, use your browser's "Add to Home Screen" feature to use the Simp App as a standalone application.
