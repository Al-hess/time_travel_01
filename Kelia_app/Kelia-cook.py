# Kelia-cook.py
# Personal recipe & activity management app for Kelia & partner.
# Streamlit app with SQLite backend. Mobile-friendly (PWA-ready via Safari).

import streamlit as st
import sqlite3
import os
from PIL import Image
import io
import base64
import datetime

# ─────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "kelia_recipes.db")

def is_postgres():
    return "supabase_cooking" in st.secrets and "url" in st.secrets["supabase_cooking"]

def get_conn():
    if is_postgres():
        import psycopg2
        return psycopg2.connect(st.secrets["supabase_cooking"]["url"])
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    if is_postgres():
        c.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id   SERIAL PRIMARY KEY,
                name          TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id     SERIAL PRIMARY KEY,
                name          TEXT NOT NULL,
                category_id   INTEGER REFERENCES categories(category_id),
                servings      INTEGER DEFAULT 2,
                prep_min      INTEGER DEFAULT 0,
                cook_min      INTEGER DEFAULT 0,
                notes         TEXT,
                favourite     INTEGER DEFAULT 0,
                author        TEXT DEFAULT '',
                image         BYTEA
            );
            CREATE TABLE IF NOT EXISTS ingredients (
                ingredient_id SERIAL PRIMARY KEY,
                recipe_id     INTEGER REFERENCES recipes(recipe_id) ON DELETE CASCADE,
                name          TEXT NOT NULL,
                qty           TEXT,
                unit          TEXT
            );
            CREATE TABLE IF NOT EXISTS steps (
                step_id       SERIAL PRIMARY KEY,
                recipe_id     INTEGER REFERENCES recipes(recipe_id) ON DELETE CASCADE,
                step_number   INTEGER,
                instruction   TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activities (
                activity_id   SERIAL PRIMARY KEY,
                name          TEXT NOT NULL,
                category      TEXT DEFAULT '',
                cost          REAL DEFAULT 0,
                duration_min  INTEGER DEFAULT 0,
                sport_value   INTEGER DEFAULT 1,
                notes         TEXT DEFAULT '',
                favourite     INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS counters (
                id            TEXT PRIMARY KEY,
                last_date     TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS movies (
                movie_id      SERIAL PRIMARY KEY,
                title         TEXT NOT NULL,
                category      TEXT NOT NULL,
                watched       INTEGER DEFAULT 0
            );
            INSERT INTO categories (name) VALUES
                ('🍝 Pasta'), ('🥗 Salads'), ('🥩 Meat'),
                ('🐟 Fish'), ('🥘 Soups & Stews'), ('🍰 Desserts'),
                ('🌮 Street Food'), ('🥞 Breakfast'), ('🍹 Drinks'), ('🥦 Vegetarian')
            ON CONFLICT DO NOTHING;
        """)
    else:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                category_id   INTEGER REFERENCES categories(category_id),
                servings      INTEGER DEFAULT 2,
                prep_min      INTEGER DEFAULT 0,
                cook_min      INTEGER DEFAULT 0,
                notes         TEXT,
                favourite     INTEGER DEFAULT 0,
                author        TEXT DEFAULT '',
                image         BLOB
            );
            CREATE TABLE IF NOT EXISTS ingredients (
                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id     INTEGER REFERENCES recipes(recipe_id) ON DELETE CASCADE,
                name          TEXT NOT NULL,
                qty           TEXT,
                unit          TEXT
            );
            CREATE TABLE IF NOT EXISTS steps (
                step_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id     INTEGER REFERENCES recipes(recipe_id) ON DELETE CASCADE,
                step_number   INTEGER,
                instruction   TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activities (
                activity_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                category      TEXT DEFAULT '',
                cost          REAL DEFAULT 0,
                duration_min  INTEGER DEFAULT 0,
                sport_value   INTEGER DEFAULT 1,
                notes         TEXT DEFAULT '',
                favourite     INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS counters (
                id            TEXT PRIMARY KEY,
                last_date     TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS movies (
                movie_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                title         TEXT NOT NULL,
                category      TEXT NOT NULL,
                watched       INTEGER DEFAULT 0
            );
            INSERT OR IGNORE INTO categories (name) VALUES
                ('🍝 Pasta'), ('🥗 Salads'), ('🥩 Meat'),
                ('🐟 Fish'), ('🥘 Soups & Stews'), ('🍰 Desserts'),
                ('🌮 Street Food'), ('🥞 Breakfast'), ('🍹 Drinks'), ('🥦 Vegetarian');
        """)
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def fetch_all(query, params=()):
    if is_postgres():
        query = query.replace("?", "%s")
        
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def execute(query, params=(), return_id=False):
    if is_postgres():
        query = query.replace("?", "%s")
        if "REPLACE INTO counters" in query:
            query = query.replace("REPLACE INTO counters", "INSERT INTO counters")
            query += " ON CONFLICT (id) DO UPDATE SET last_date = EXCLUDED.last_date"
        if return_id:
            query += " RETURNING recipe_id"
            
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    
    last_id = None
    if return_id:
        if is_postgres():
            last_id = c.fetchone()[0]
        else:
            last_id = c.lastrowid
            
    conn.commit()
    conn.close()
    return last_id

def get_categories():
    return fetch_all("SELECT category_id, name FROM categories ORDER BY name")

def get_recipes(favourite_only=False, category_id=None, search=""):
    query = """
        SELECT r.recipe_id, r.name, c.name, r.servings,
               r.prep_min, r.cook_min, r.favourite, r.author, r.image
        FROM recipes r
        LEFT JOIN categories c ON r.category_id = c.category_id
        WHERE 1=1
    """
    params = []
    if favourite_only:
        query += " AND r.favourite = 1"
    if category_id:
        query += " AND r.category_id = ?"
        params.append(category_id)
    if search:
        query += " AND LOWER(r.name) LIKE ?"
        params.append(f"%{search.lower()}%")
    query += " ORDER BY r.name"
    return fetch_all(query, params)

def get_recipe_detail(recipe_id):
    r = fetch_all("""
        SELECT r.recipe_id, r.name, c.name, r.servings,
               r.prep_min, r.cook_min, r.notes, r.favourite, r.author, r.image
        FROM recipes r LEFT JOIN categories c ON r.category_id = c.category_id
        WHERE r.recipe_id = ?
    """, (recipe_id,))
    ingredients = fetch_all(
        "SELECT name, qty, unit FROM ingredients WHERE recipe_id = ? ORDER BY ingredient_id",
        (recipe_id,)
    )
    steps = fetch_all(
        "SELECT step_number, instruction FROM steps WHERE recipe_id = ? ORDER BY step_number",
        (recipe_id,)
    )
    return r[0] if r else None, ingredients, steps

def toggle_favourite(recipe_id, current):
    execute("UPDATE recipes SET favourite = ? WHERE recipe_id = ?", (0 if current else 1, recipe_id))

def delete_recipe(recipe_id):
    execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
    execute("DELETE FROM steps WHERE recipe_id = ?", (recipe_id,))
    execute("DELETE FROM recipes WHERE recipe_id = ?", (recipe_id,))

def img_to_b64(blob):
    if blob:
        return base64.b64encode(blob).decode()
    return None

# Activities helpers
def get_activities(search="", category="All", fav_only=False):
    query = "SELECT activity_id, name, category, cost, duration_min, sport_value, notes, favourite FROM activities WHERE 1=1"
    params = []
    if fav_only:
        query += " AND favourite = 1"
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND LOWER(name) LIKE ?"
        params.append(f"%{search.lower()}%")
    query += " ORDER BY name"
    return fetch_all(query, params)

def toggle_activity_favourite(activity_id, current):
    execute("UPDATE activities SET favourite = ? WHERE activity_id = ?", (0 if current else 1, activity_id))

def delete_activity(activity_id):
    execute("DELETE FROM activities WHERE activity_id = ?", (activity_id,))

ACTIVITY_CATEGORIES = [
    "🏃 Outdoor", "🏋️ Sport", "🎨 Creative", "🎲 Games",
    "🎬 Entertainment", "🍽️ Food & Drink", "✈️ Travel", "🧘 Wellness", "📚 Learning", "🛍️ Shopping"
]

MOVIE_CATEGORIES = [
    "🍿 Action", "😂 Comedy", "🎞️ Drama", "🥺 Romance", 
    "🤯 Sci-Fi", "🧙 Fantasy", "😱 Horror", "🕵️ Thriller", 
    "🎬 Documentary", "🦸 Superhero", "🐉 Animation", "🤷 Other"
]

def get_counter(counter_id):
    row = fetch_all("SELECT last_date FROM counters WHERE id = ?", (counter_id,))
    if row:
        return datetime.datetime.fromisoformat(row[0][0])
    return None

# ─────────────────────────────────────────
#  PAGE CONFIG & STYLING
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Simp App",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFF8F2;
    }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 780px; }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* ── Title ── */
    .app-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #C0392B;
        text-align: center;
        margin-bottom: 0;
        line-height: 1.1;
    }
    .app-sub {
        text-align: center;
        color: #A0522D;
        font-size: 0.85rem;
        margin-top: 0.15rem;
        margin-bottom: 1.2rem;
        opacity: 0.8;
    }

    /* ── Top-level tabs (Cooking / Activities) ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #FEF0E7;
        border-radius: 16px;
        gap: 4px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #A0522D;
        padding: 6px 14px;
    }
    .stTabs [aria-selected="true"] {
        background: #C0392B !important;
        color: white !important;
    }

    /* ── Recipe Card ── */
    .recipe-card {
        background: white;
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(192,57,43,0.08);
        border: 1.5px solid #F5E6DC;
        cursor: pointer;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .recipe-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(192,57,43,0.15); }
    .recipe-card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.15rem;
        color: #2C1A10;
        margin: 0 0 4px 0;
    }
    .recipe-card-meta {
        font-size: 0.78rem;
        color: #A0522D;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        align-items: center;
    }
    .fav-badge { color: #E74C3C; font-size: 1.1rem; }
    .cat-badge {
        background: #FEF0E7;
        color: #C0392B;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.73rem;
        font-weight: 600;
    }

    /* ── Activity Card ── */
    .activity-card {
        background: white;
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(52,152,219,0.08);
        border: 1.5px solid #D6EAF8;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .activity-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(52,152,219,0.15); }
    .sport-bar-bg {
        background: #EBF5FB;
        border-radius: 8px;
        height: 8px;
        width: 100%;
        margin-top: 6px;
    }
    .sport-bar-fill {
        background: linear-gradient(90deg, #2980B9, #1ABC9C);
        border-radius: 8px;
        height: 8px;
    }

    /* ── Detail ── */
    .detail-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.9rem;
        color: #2C1A10;
        margin-bottom: 0.2rem;
    }
    .detail-meta { color: #A0522D; font-size: 0.88rem; margin-bottom: 1rem; }
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.15rem;
        color: #C0392B;
        border-bottom: 2px solid #F5E6DC;
        padding-bottom: 4px;
        margin: 1.2rem 0 0.6rem;
    }
    .step-pill {
        background: #C0392B;
        color: white;
        border-radius: 50%;
        width: 26px; height: 26px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
        margin-right: 10px;
    }
    .step-row {
        display: flex;
        align-items: flex-start;
        gap: 4px;
        padding: 8px 0;
        border-bottom: 1px solid #F5E6DC;
        color: #2C1A10;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        border: none;
    }
    div[data-testid="column"] .stButton > button {
        width: 100%;
    }

    /* ── Inputs ── */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div {
        border-radius: 10px !important;
        border-color: #F5E6DC !important;
        background: white !important;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        color: #C0A090;
        padding: 3rem 1rem;
        font-size: 1rem;
    }
    .empty-state .emoji { font-size: 3rem; display: block; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────

for key, default in [
    ("view_recipe_id", None),
    ("edit_recipe_id", None),
    ("ingredient_count", 3),
    ("step_count", 3),
    ("view_activity_id", None),
    ("edit_activity_id", None),
    ("confirm_delete", False),
    ("confirm_delete_activity", False),
    ("flash_msg", None),
    ("flash_balloons", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────

st.markdown('<div class="app-title">🌸 Simp App</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">We are cooked chat 🍳 🏃</div>', unsafe_allow_html=True)

if not is_postgres():
    st.warning("⚠️ **Warning:** The app is currently using a local, temporary database. Any recipes you add will be deleted when the server goes to sleep. Please configure the PostgreSQL secrets in Streamlit Cloud to save your data permanently.")

if st.session_state.get("flash_msg"):
    st.toast(st.session_state.flash_msg, icon="✅")
    st.session_state.flash_msg = None

if st.session_state.get("flash_balloons"):
    st.balloons()
    st.session_state.flash_balloons = False

# ─────────────────────────────────────────
#  RECIPE DETAIL VIEW
# ─────────────────────────────────────────

def show_detail(recipe_id):
    recipe, ingredients, steps = get_recipe_detail(recipe_id)
    if not recipe:
        st.error("Recipe not found.")
        st.session_state.view_recipe_id = None
        st.rerun()
        return

    rid, name, cat, servings, prep, cook, notes, fav, author, image = recipe

    if st.button("← Back to recipes"):
        st.session_state.view_recipe_id = None
        st.rerun()

    if image:
        b64 = img_to_b64(image)
        st.markdown(f'<img src="data:image/jpeg;base64,{b64}" style="width:100%;border-radius:18px;max-height:260px;object-fit:cover;margin-bottom:1rem;">', unsafe_allow_html=True)

    fav_icon = "❤️" if fav else "🤍"
    st.markdown(f'<div class="detail-title">{name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-meta">{cat or ""}  ·  🍽 {servings} servings  ·  ⏱ {prep + cook} min total{("  ·  by " + author) if author else ""}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if st.button(f"{fav_icon} Favourite", key="fav_btn"):
            toggle_favourite(rid, fav)
            st.rerun()
    with col2:
        if st.button("✏️ Edit", key="edit_btn"):
            _clear_recipe_form()
            st.session_state.edit_recipe_id = rid
            st.session_state.view_recipe_id = None
            st.rerun()
    with col3:
        if st.button("🗑️ Delete", key="del_btn"):
            st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete"):
        st.warning(f"Delete **{name}**? This cannot be undone.")
        ca, cb = st.columns(2)
        with ca:
            if st.button("Yes, delete", type="primary"):
                delete_recipe(rid)
                st.session_state.view_recipe_id = None
                st.session_state.confirm_delete = False
                st.session_state.flash_msg = "Recipe deleted."
                st.rerun()
        with cb:
            if st.button("Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

    c1, c2, c3 = st.columns(3)
    c1.metric("Prep", f"{prep} min")
    c2.metric("Cook", f"{cook} min")
    c3.metric("Servings", servings)

    st.markdown('<div class="section-header">🛒 Ingredients</div>', unsafe_allow_html=True)
    if ingredients:
        for ing in ingredients:
            ing_name, qty, unit = ing
            label = f"**{qty or ''} {unit or ''}** {ing_name}".strip()
            st.checkbox(label, key=f"ing_{rid}_{ing_name}")
    else:
        st.caption("No ingredients listed.")

    st.markdown('<div class="section-header">👨‍🍳 Steps</div>', unsafe_allow_html=True)
    if steps:
        for step in steps:
            st.markdown(
                f'<div class="step-row"><span class="step-pill">{step[0]}</span><span>{step[1]}</span></div>',
                unsafe_allow_html=True
            )
    else:
        st.caption("No steps listed.")

    if notes:
        st.markdown('<div class="section-header">📝 Notes</div>', unsafe_allow_html=True)
        st.info(notes)


# ─────────────────────────────────────────
#  ADD / EDIT FORM  (ingredients & steps
#  are stored in session_state so they
#  survive the rerun from "+ Add Row")
# ─────────────────────────────────────────

def _ss_form_key(suffix):
    """Return a session-state key namespaced to the recipe form."""
    return f"rf_{suffix}"

def _init_recipe_form(prefill):
    """Populate session-state form keys only once (first render)."""
    ss = st.session_state
    k = _ss_form_key

    # Basic fields – only set if the key doesn't exist yet
    if k("name")    not in ss: ss[k("name")]    = prefill["name"]
    if k("author")  not in ss: ss[k("author")]  = prefill["author"]
    if k("new_cat") not in ss: ss[k("new_cat")]  = ""
    if k("notes")   not in ss: ss[k("notes")]    = prefill["notes"]
    if k("servings")not in ss: ss[k("servings")] = prefill["servings"]
    if k("prep")    not in ss: ss[k("prep")]     = prefill["prep"]
    if k("cook")    not in ss: ss[k("cook")]     = prefill["cook"]

    # Ingredients
    n_ing = ss.ingredient_count
    if k("ing_count") not in ss:
        ss[k("ing_count")] = max(n_ing, len(prefill["ingredients"]))
    for i in range(ss[k("ing_count")]):
        if k(f"iname_{i}") not in ss:
            ss[k(f"iname_{i}")] = prefill["ingredients"][i][0] if i < len(prefill["ingredients"]) else ""
        if k(f"iqty_{i}") not in ss:
            ss[k(f"iqty_{i}")] = prefill["ingredients"][i][1] if i < len(prefill["ingredients"]) else ""
        if k(f"iunit_{i}") not in ss:
            ss[k(f"iunit_{i}")] = prefill["ingredients"][i][2] if i < len(prefill["ingredients"]) else ""

    # Steps
    n_step = ss.step_count
    if k("step_count") not in ss:
        ss[k("step_count")] = max(n_step, len(prefill["steps"]))
    for i in range(ss[k("step_count")]):
        if k(f"step_{i}") not in ss:
            ss[k(f"step_{i}")] = prefill["steps"][i] if i < len(prefill["steps"]) else ""

def _clear_recipe_form():
    """Remove all recipe form keys from session state."""
    ss = st.session_state
    keys_to_del = [key for key in ss if key.startswith("rf_")]
    for key in keys_to_del:
        del ss[key]


def show_recipe_form(edit_id=None):
    """Render the add/edit recipe form."""
    is_edit = edit_id is not None

    prefill = {"name": "", "category": None, "servings": 2, "prep": 10, "cook": 20,
               "author": "", "notes": "", "ingredients": [], "steps": []}
    if is_edit:
        recipe, ingredients, steps = get_recipe_detail(edit_id)
        if recipe:
            rid, name, cat, servings, prep, cook, notes, fav, author, image = recipe
            prefill = {"name": name, "category": cat, "servings": servings,
                       "prep": prep, "cook": cook, "author": author or "",
                       "notes": notes or "",
                       "ingredients": [(i[0], i[1] or "", i[2] or "") for i in ingredients],
                       "steps": [s[1] for s in steps]}

    # Seed session state (only first time for this form)
    _init_recipe_form(prefill)

    ss = st.session_state
    k  = _ss_form_key

    st.subheader("✏️ Edit Recipe" if is_edit else "➕ New Recipe")
    if is_edit and st.button("← Cancel"):
        _clear_recipe_form()
        ss.edit_recipe_id = None
        st.rerun()

    categories = get_categories()
    cat_names = [c[1] for c in categories]
    cat_map = {c[1]: c[0] for c in categories}

    # ── Basic fields ──
    name   = st.text_input("Recipe Name *", key=k("name"), placeholder="e.g. Grandma's Risotto")
    author = st.text_input("Added by",      key=k("author"), placeholder="Name")

    col_cat, col_new = st.columns([3, 2])
    with col_cat:
        default_cat_idx = cat_names.index(prefill["category"]) if prefill["category"] in cat_names else 0
        sel_cat = st.selectbox("Category", cat_names, index=default_cat_idx, key=k("sel_cat"))
    with col_new:
        new_cat = st.text_input("Or create new category", key=k("new_cat"), placeholder="e.g. 🫕 Stews")

    col_s, col_p, col_c = st.columns(3)
    with col_s: st.number_input("Servings",   1,   20, key=k("servings"))
    with col_p: st.number_input("Prep (min)", 0,  600, key=k("prep"))
    with col_c: st.number_input("Cook (min)", 0,  600, key=k("cook"))

    uploaded = st.file_uploader("📷 Photo (optional)", type=["jpg", "jpeg", "png"], key="form_photo")
    st.text_area("📝 Notes / Tips", key=k("notes"), placeholder="Any extra tips, substitutions…", height=80)

    # ── Ingredients ──
    st.markdown("### 🛒 Ingredients")
    # Initialize ingredients list for data_editor
    if k("ing_data") not in ss:
        ing_data = [{"Ingredient": i[0], "Qty": i[1], "Unit": i[2]} for i in prefill["ingredients"]]
        while len(ing_data) < 3:
            ing_data.append({"Ingredient": "", "Qty": "", "Unit": ""})
        ss[k("ing_data")] = ing_data

    edited_ings = st.data_editor(
        ss[k("ing_data")],
        num_rows="dynamic",
        column_config={
            "Ingredient": st.column_config.TextColumn("Ingredient", required=True, width="large"),
            "Qty": st.column_config.TextColumn("Qty", width="small"),
            "Unit": st.column_config.TextColumn("Unit", width="small"),
        },
        use_container_width=True,
        hide_index=True,
        key=k("ing_editor")
    )

    # ── Steps ──
    st.markdown("### 👨‍🍳 Steps")
    if k("step_data") not in ss:
        step_data = [{"Instruction": s} for s in prefill["steps"]]
        while len(step_data) < 3:
            step_data.append({"Instruction": ""})
        ss[k("step_data")] = step_data

    edited_steps = st.data_editor(
        ss[k("step_data")],
        num_rows="dynamic",
        column_config={
            "Instruction": st.column_config.TextColumn("Instruction", required=True, width="large"),
        },
        use_container_width=True,
        hide_index=True,
        key=k("step_editor")
    )

    st.divider()
    # Adding a note to reassure the user
    st.info("💡 Hitting 'Enter' on your keyboard saves your typing. A recipe is ONLY saved when you click the button below.")
    submitted = st.button("💾 Save Recipe", type="primary", use_container_width=True, key="save_recipe_btn")

    if submitted:
        final_name   = ss.get(k("name"), "").strip()
        final_author = ss.get(k("author"), "").strip()
        final_new_cat= ss.get(k("new_cat"), "").strip()
        final_sel_cat= ss.get(k("sel_cat"), cat_names[0] if cat_names else "")
        final_servings = ss.get(k("servings"), 2)
        final_prep   = ss.get(k("prep"), 0)
        final_cook   = ss.get(k("cook"), 0)
        final_notes  = ss.get(k("notes"), "").strip()

        if not final_name:
            st.error("⚠️ Recipe name is required!")
            return

        final_cat_name = final_new_cat if final_new_cat else final_sel_cat
        if final_new_cat:
            if is_postgres():
                execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (final_cat_name,))
            else:
                execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (final_cat_name,))
        cat_id = fetch_all("SELECT category_id FROM categories WHERE name = ?", (final_cat_name,))
        cat_id = cat_id[0][0] if cat_id else None

        image_blob = None
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            image_blob = buf.getvalue()

        ing_rows = []
        for row in edited_ings:
            iname = str(row.get("Ingredient", "")).strip()
            iqty  = str(row.get("Qty", "")).strip()
            iunit = str(row.get("Unit", "")).strip()
            if iname:
                ing_rows.append((iname, iqty, iunit))

        step_rows = []
        for row in edited_steps:
            stext = str(row.get("Instruction", "")).strip()
            if stext:
                step_rows.append(stext)

        if is_edit:
            execute("""UPDATE recipes SET name=?, category_id=?, servings=?, prep_min=?,
                       cook_min=?, notes=?, author=? WHERE recipe_id=?""",
                    (final_name, cat_id, final_servings, final_prep, final_cook, final_notes, final_author, edit_id))
            if image_blob:
                execute("UPDATE recipes SET image=? WHERE recipe_id=?", (image_blob, edit_id))
            execute("DELETE FROM ingredients WHERE recipe_id=?", (edit_id,))
            execute("DELETE FROM steps WHERE recipe_id=?", (edit_id,))
            recipe_id = edit_id
        else:
            recipe_id = execute(
                "INSERT INTO recipes (name, category_id, servings, prep_min, cook_min, notes, author, image) VALUES (?,?,?,?,?,?,?,?)",
                (final_name, cat_id, final_servings, final_prep, final_cook, final_notes, final_author, image_blob),
                return_id=True
            )

        for iname, iqty, iunit in ing_rows:
            if iname:
                execute("INSERT INTO ingredients (recipe_id, name, qty, unit) VALUES (?,?,?,?)",
                        (recipe_id, iname, iqty, iunit))

        for idx, stext in enumerate(step_rows, 1):
            if stext:
                execute("INSERT INTO steps (recipe_id, step_number, instruction) VALUES (?,?,?)",
                        (recipe_id, idx, stext))

        _clear_recipe_form()
        ss.edit_recipe_id = None
        st.session_state.flash_msg = f"Recipe **{final_name}** saved!"
        st.session_state.flash_balloons = True
        st.rerun()


# ─────────────────────────────────────────
#  RECIPE CARDS
# ─────────────────────────────────────────

def show_recipe_cards(recipes, prefix=""):
    if not recipes:
        st.markdown('<div class="empty-state"><span class="emoji">🍽️</span>No recipes here yet.<br>Add your first one!</div>', unsafe_allow_html=True)
        return

    for row in recipes:
        rid, rname, rcat, rservings, rprep, rcook, rfav, rauthor, rimage = row
        total_time = rprep + rcook
        fav_icon = "❤️" if rfav else ""

        with st.container():
            st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**{rname}** {fav_icon}", unsafe_allow_html=True)
                meta_parts = []
                if rcat: meta_parts.append(rcat)
                if total_time: meta_parts.append(f"⏱ {total_time} min")
                if rservings: meta_parts.append(f"🍽 {rservings}")
                if rauthor: meta_parts.append(f"by {rauthor}")
                st.caption("  ·  ".join(meta_parts))
            with cols[1]:
                if st.button("Open →", key=f"open_{prefix}_{rid}"):
                    st.session_state.view_recipe_id = rid
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
#  ACTIVITY FORM
# ─────────────────────────────────────────

def show_activity_form(edit_id=None):
    """Render the add/edit activity form."""
    is_edit = edit_id is not None
    prefill = {"name": "", "category": ACTIVITY_CATEGORIES[0], "cost": 0.0,
               "duration": 60, "sport_value": 3, "notes": ""}

    if is_edit:
        row = fetch_all("SELECT * FROM activities WHERE activity_id = ?", (edit_id,))
        if row:
            aid, name, cat, cost, dur, sv, notes, fav = row[0]
            prefill = {"name": name, "category": cat or ACTIVITY_CATEGORIES[0],
                       "cost": float(cost), "duration": int(dur),
                       "sport_value": int(sv), "notes": notes or ""}

    st.subheader("✏️ Edit Activity" if is_edit else "➕ New Activity")
    if is_edit and st.button("← Cancel", key="act_cancel"):
        st.session_state.edit_activity_id = None
        st.rerun()

    act_name = st.text_input("Activity Name *", value=prefill["name"],
                             placeholder="e.g. Morning Run", key="act_name")

    cat_idx = ACTIVITY_CATEGORIES.index(prefill["category"]) if prefill["category"] in ACTIVITY_CATEGORIES else 0
    act_cat = st.selectbox("Category", ACTIVITY_CATEGORIES, index=cat_idx, key="act_cat")

    col_cost, col_dur, col_sv = st.columns(3)
    with col_cost:
        act_cost = st.number_input("💶 Cost (€)", min_value=0.0, step=0.5,
                                   value=prefill["cost"], key="act_cost")
    with col_dur:
        act_dur = st.number_input("⏱ Duration (min)", min_value=0, step=5,
                                  value=prefill["duration"], key="act_dur")
    with col_sv:
        act_sv = st.slider("🏅 Sport value", 1, 5, value=prefill["sport_value"], key="act_sv",
                           help="1 = relaxed, 5 = intense workout")

    st.caption(f"Sport intensity: {'🟢' * act_sv}{'⚫' * (5 - act_sv)}")
    act_notes = st.text_area("📝 Notes", value=prefill["notes"],
                             placeholder="Any details, links, tips…", height=80, key="act_notes")

    st.divider()
    if st.button("💾 Save Activity", type="primary", use_container_width=True, key="save_act_btn"):
        if not act_name.strip():
            st.error("⚠️ Activity name is required!")
            return
        if is_edit:
            execute("""UPDATE activities SET name=?, category=?, cost=?, duration_min=?,
                       sport_value=?, notes=? WHERE activity_id=?""",
                    (act_name.strip(), act_cat, act_cost, act_dur, act_sv, act_notes.strip(), edit_id))
        else:
            execute("""INSERT INTO activities (name, category, cost, duration_min, sport_value, notes)
                       VALUES (?,?,?,?,?,?)""",
                    (act_name.strip(), act_cat, act_cost, act_dur, act_sv, act_notes.strip()))
        st.session_state.edit_activity_id = None
        st.session_state.flash_msg = f"Activity **{act_name.strip()}** saved!"
        st.session_state.flash_balloons = True
        st.rerun()


# ─────────────────────────────────────────
#  ACTIVITY CARDS
# ─────────────────────────────────────────

def show_activity_cards(activities, prefix=""):
    if not activities:
        st.markdown('<div class="empty-state"><span class="emoji">🏃</span>No activities yet.<br>Add your first one!</div>', unsafe_allow_html=True)
        return

    for row in activities:
        aid, aname, acat, acost, adur, asv, anotes, afav = row
        fav_icon = "❤️" if afav else ""

        with st.container():
            st.markdown('<div class="activity-card">', unsafe_allow_html=True)
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**{aname}** {fav_icon}", unsafe_allow_html=True)
                meta = []
                if acat:  meta.append(acat)
                if adur:  meta.append(f"⏱ {adur} min")
                if acost: meta.append(f"💶 €{acost:.0f}")
                st.caption("  ·  ".join(meta))
                # Sport value bar
                pct = int(asv / 5 * 100)
                st.markdown(
                    f'<div class="sport-bar-bg"><div class="sport-bar-fill" style="width:{pct}%;"></div></div>'
                    f'<small style="color:#7F8C8D">Sport: {"🏅"*asv}{"·"*(5-asv)}</small>',
                    unsafe_allow_html=True
                )
            with cols[1]:
                if st.button("Open →", key=f"act_open_{prefix}_{aid}"):
                    st.session_state.view_activity_id = aid
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
#  ACTIVITY DETAIL
# ─────────────────────────────────────────

def show_activity_detail(activity_id):
    rows = fetch_all("SELECT * FROM activities WHERE activity_id = ?", (activity_id,))
    if not rows:
        st.error("Activity not found.")
        st.session_state.view_activity_id = None
        st.rerun()
        return

    aid, name, cat, cost, dur, sv, notes, fav = rows[0]

    if st.button("← Back to activities"):
        st.session_state.view_activity_id = None
        st.rerun()

    fav_icon = "❤️" if fav else "🤍"
    st.markdown(f'<div class="detail-title">{name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-meta">{cat or ""}  ·  ⏱ {dur} min  ·  💶 €{cost:.2f}</div>', unsafe_allow_html=True)

    pct = int(sv / 5 * 100)
    st.markdown(
        f'<div class="sport-bar-bg"><div class="sport-bar-fill" style="width:{pct}%;"></div></div>'
        f'<small style="color:#7F8C8D">Sport intensity: {"🏅"*sv}{"·"*(5-sv)} ({sv}/5)</small>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Duration", f"{dur} min")
    col2.metric("Cost", f"€{cost:.2f}")
    col3.metric("Sport value", f"{sv}/5")

    btn1, btn2, btn3 = st.columns([2, 2, 2])
    with btn1:
        if st.button(f"{fav_icon} Favourite", key="act_fav_btn"):
            toggle_activity_favourite(aid, fav)
            st.rerun()
    with btn2:
        if st.button("✏️ Edit", key="act_edit_btn"):
            st.session_state.edit_activity_id = aid
            st.session_state.view_activity_id = None
            st.rerun()
    with btn3:
        if st.button("🗑️ Delete", key="act_del_btn"):
            st.session_state.confirm_delete_activity = True

    if st.session_state.get("confirm_delete_activity"):
        st.warning(f"Delete **{name}**? This cannot be undone.")
        ca, cb = st.columns(2)
        with ca:
            if st.button("Yes, delete", type="primary", key="act_yes_del"):
                delete_activity(aid)
                st.session_state.view_activity_id = None
                st.session_state.confirm_delete_activity = False
                st.session_state.flash_msg = "Activity deleted."
                st.rerun()
        with cb:
            if st.button("Cancel", key="act_cancel_del"):
                st.session_state.confirm_delete_activity = False
                st.rerun()

    if notes:
        st.markdown('<div class="section-header">📝 Notes</div>', unsafe_allow_html=True)
        st.info(notes)


# ─────────────────────────────────────────
#  TOP-LEVEL ROUTING
# ─────────────────────────────────────────

# Detail / edit views take over the whole screen
if st.session_state.view_recipe_id:
    show_detail(st.session_state.view_recipe_id)

elif st.session_state.edit_recipe_id:
    show_recipe_form(edit_id=st.session_state.edit_recipe_id)

elif st.session_state.view_activity_id:
    show_activity_detail(st.session_state.view_activity_id)

elif st.session_state.edit_activity_id:
    show_activity_form(edit_id=st.session_state.edit_activity_id)

else:
    # ── FOUR TOP-LEVEL TABS ──
    tab_cooking, tab_activities, tab_us, tab_movies = st.tabs(["🍳 Cooking", "🏃 Activities", "Rat counter 🐀", "🍿 Movies"])

    # ════════════════════════════════════════
    #  COOKING TAB
    # ════════════════════════════════════════
    with tab_cooking:
        sub_browse, sub_add, sub_favs = st.tabs(["🏠 Browse", "➕ Add Recipe", "❤️ Favourites"])

        with sub_browse:
            search = st.text_input("🔍 Search recipes…", placeholder="e.g. pasta, risotto…",
                                   label_visibility="collapsed", key="cook_search")
            categories = get_categories()
            cat_names = ["All"] + [c[1] for c in categories]
            cat_map = {c[1]: c[0] for c in categories}
            sel_filter = st.selectbox("Filter by category", cat_names,
                                      label_visibility="collapsed", key="cook_filter")
            filter_cat_id = cat_map.get(sel_filter) if sel_filter != "All" else None
            recipes = get_recipes(favourite_only=False, category_id=filter_cat_id, search=search)
            total = len(recipes)
            st.caption(f"{total} recipe{'s' if total != 1 else ''} found")
            show_recipe_cards(recipes, prefix="browse")

        with sub_add:
            show_recipe_form()

        with sub_favs:
            fav_recipes = get_recipes(favourite_only=True)
            if not fav_recipes:
                st.markdown('<div class="empty-state"><span class="emoji">❤️</span>No favourites yet.<br>Open a recipe and tap ❤️ Favourite.</div>', unsafe_allow_html=True)
            else:
                show_recipe_cards(fav_recipes, prefix="fav")

    # ════════════════════════════════════════
    #  ACTIVITIES TAB
    # ════════════════════════════════════════
    with tab_activities:
        sub_act_browse, sub_act_add, sub_act_favs = st.tabs(["🔍 Browse", "➕ Add Activity", "❤️ Favourites"])

        with sub_act_browse:
            act_search = st.text_input("🔍 Search activities…", placeholder="e.g. hiking, yoga…",
                                       label_visibility="collapsed", key="act_search")
            cat_filter_opts = ["All"] + ACTIVITY_CATEGORIES
            act_cat_filter = st.selectbox("Filter by category", cat_filter_opts,
                                          label_visibility="collapsed", key="act_cat_filter")
            act_filter_val = act_cat_filter if act_cat_filter != "All" else ""

            activities = get_activities(search=act_search, category=act_filter_val)
            st.caption(f"{len(activities)} activit{'ies' if len(activities) != 1 else 'y'} found")
            show_activity_cards(activities, prefix="browse")

        with sub_act_add:
            show_activity_form()

        with sub_act_favs:
            fav_acts = get_activities(fav_only=True)
            if not fav_acts:
                st.markdown('<div class="empty-state"><span class="emoji">❤️</span>No favourite activities yet.<br>Open one and tap ❤️ Favourite.</div>', unsafe_allow_html=True)
            else:
                show_activity_cards(fav_acts, prefix="fav")

    # ════════════════════════════════════════
    #  US TAB (COUNTERS)
    # ════════════════════════════════════════
    with tab_us:
        # Initialize default counters if missing
        now = datetime.datetime.now()
        for cid in ["last_date", "last_flowers"]:
            if not get_counter(cid):
                execute("REPLACE INTO counters (id, last_date) VALUES (?, ?)", (cid, now.isoformat()))

        last_date = get_counter("last_date")
        last_flowers = get_counter("last_flowers")
        
        days_date = (now.date() - last_date.date()).days if last_date else 0
        days_flowers = (now.date() - last_flowers.date()).days if last_flowers else 0
        
        st.markdown('<div class="section-header">💑 Rat Trackers 🐀</div>', unsafe_allow_html=True)
        
        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="activity-card" style="text-align: center;">', unsafe_allow_html=True)
            st.markdown("<div style='font-size: 1rem; font-weight: 600; color: #A0522D; margin-bottom: 8px;'>Last Date 🍷</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #C0392B; font-size: 3.5rem; font-weight: 700; line-height: 1;'>{days_date}</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.8rem; color: #A0522D; margin-bottom: 16px;'>days ago</div>", unsafe_allow_html=True)
            if st.button("Restart 🍷", use_container_width=True, key="res_date"):
                execute("REPLACE INTO counters (id, last_date) VALUES (?, ?)", ("last_date", datetime.datetime.now().isoformat()))
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with cb:
            st.markdown('<div class="activity-card" style="text-align: center;">', unsafe_allow_html=True)
            st.markdown("<div style='font-size: 1rem; font-weight: 600; color: #A0522D; margin-bottom: 8px;'>Flowers 💐</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #C0392B; font-size: 3.5rem; font-weight: 700; line-height: 1;'>{days_flowers}</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.8rem; color: #A0522D; margin-bottom: 16px;'>days ago</div>", unsafe_allow_html=True)
            if st.button("Restart 💐", use_container_width=True, key="res_flow"):
                execute("REPLACE INTO counters (id, last_date) VALUES (?, ?)", ("last_flowers", datetime.datetime.now().isoformat()))
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    #  MOVIES TAB
    # ════════════════════════════════════════
    with tab_movies:
        st.markdown('<div class="section-header">🍿 Movie List</div>', unsafe_allow_html=True)
        
        with st.expander("➕ Add New Movie", expanded=True):
            with st.form("add_movie_form", clear_on_submit=True):
                mc1, mc2 = st.columns([2, 1])
                with mc1:
                    m_title = st.text_input("Movie Title", placeholder="e.g. Inception")
                with mc2:
                    m_cat = st.selectbox("Category", MOVIE_CATEGORIES)
                    
                if st.form_submit_button("💾 Save Movie", use_container_width=True, type="primary"):
                    if m_title.strip():
                        execute("INSERT INTO movies (title, category, watched) VALUES (?, ?, 0)", (m_title.strip(), m_cat))
                        st.rerun()
                    else:
                        st.error("⚠️ Movie title is required!")

        st.markdown('<div class="section-header">📺 To Watch</div>', unsafe_allow_html=True)
        movies_to_watch = fetch_all("SELECT movie_id, title, category FROM movies WHERE watched = 0 ORDER BY movie_id DESC")
        
        if not movies_to_watch:
            st.caption("No movies in your watchlist. Time to add some!")
        else:
            for mid, mtitle, mcat in movies_to_watch:
                with st.container():
                    c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
                    with c1:
                        if st.button("✅", key=f"mcheck_{mid}", help="Mark as watched"):
                            execute("UPDATE movies SET watched = 1 WHERE movie_id = ?", (mid,))
                            st.rerun()
                    with c2:
                        st.markdown(f"<div style='padding-top: 6px;'><b>{mtitle}</b></div>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"<div style='padding-top: 6px; color: #A0522D; font-size: 0.85rem;'>{mcat}</div>", unsafe_allow_html=True)
                    with c4:
                        if st.button("🗑️", key=f"mdel_{mid}"):
                            execute("DELETE FROM movies WHERE movie_id = ?", (mid,))
                            st.rerun()
                            
        st.write("")
        with st.expander("👀 Already Watched"):
            watched_movies = fetch_all("SELECT movie_id, title, category FROM movies WHERE watched = 1 ORDER BY movie_id DESC")
            if not watched_movies:
                st.caption("Nothing watched yet.")
            else:
                for mid, mtitle, mcat in watched_movies:
                    with st.container():
                        c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
                        with c1:
                            if st.button("↺", key=f"muncheck_{mid}", help="Move back to watchlist"):
                                execute("UPDATE movies SET watched = 0 WHERE movie_id = ?", (mid,))
                                st.rerun()
                        with c2:
                            st.markdown(f"<div style='padding-top: 6px; text-decoration: line-through; color: gray;'>{mtitle}</div>", unsafe_allow_html=True)
                        with c3:
                            st.markdown(f"<div style='padding-top: 6px; color: #C0A090; font-size: 0.85rem;'>{mcat}</div>", unsafe_allow_html=True)
                        with c4:
                            if st.button("🗑️", key=f"mdelw_{mid}"):
                                execute("DELETE FROM movies WHERE movie_id = ?", (mid,))
                                st.rerun()
