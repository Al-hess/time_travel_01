# Kelia-cook.py
# Personal recipe management app for Kelia & partner.
# Streamlit app with SQLite backend. Mobile-friendly (PWA-ready via Safari).

import streamlit as st
import sqlite3
import os
from PIL import Image
import io
import base64

# ─────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "kelia_recipes.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
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
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def execute(query, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
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

# ─────────────────────────────────────────
#  PAGE CONFIG & STYLING
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Cook 🍳",
    page_icon="🍳",
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
    /* Ensure the header area doesn't clip the app title */
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

    /* ── Tabs ── */
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
    .recipe-card-img {
        width: 100%; height: 130px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 10px;
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

if "view_recipe_id" not in st.session_state:
    st.session_state.view_recipe_id = None
if "edit_recipe_id" not in st.session_state:
    st.session_state.edit_recipe_id = None
if "ingredient_count" not in st.session_state:
    st.session_state.ingredient_count = 3
if "step_count" not in st.session_state:
    st.session_state.step_count = 3
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────

st.markdown('<div class="app-title">🍳 Kelia Cook</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub"> We\'re cooked chat</div>', unsafe_allow_html=True)

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

    # Image
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
                st.success("Recipe deleted.")
                st.rerun()
        with cb:
            if st.button("Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()

    # Info pills
    c1, c2, c3 = st.columns(3)
    c1.metric("Prep", f"{prep} min")
    c2.metric("Cook", f"{cook} min")
    c3.metric("Servings", servings)

    # Ingredients
    st.markdown('<div class="section-header">🛒 Ingredients</div>', unsafe_allow_html=True)
    if ingredients:
        for ing in ingredients:
            ing_name, qty, unit = ing
            label = f"**{qty or ''} {unit or ''}** {ing_name}".strip()
            st.checkbox(label, key=f"ing_{rid}_{ing_name}")
    else:
        st.caption("No ingredients listed.")

    # Steps
    st.markdown('<div class="section-header">👨‍🍳 Steps</div>', unsafe_allow_html=True)
    if steps:
        for step in steps:
            st.markdown(
                f'<div class="step-row"><span class="step-pill">{step[0]}</span><span>{step[1]}</span></div>',
                unsafe_allow_html=True
            )
    else:
        st.caption("No steps listed.")

    # Notes
    if notes:
        st.markdown('<div class="section-header">📝 Notes</div>', unsafe_allow_html=True)
        st.info(notes)


# ─────────────────────────────────────────
#  ADD / EDIT FORM
# ─────────────────────────────────────────

def show_recipe_form(edit_id=None):
    """Render the add/edit recipe form. edit_id = None means ADD mode."""
    is_edit = edit_id is not None

    # Pre-fill values for edit mode
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

    st.subheader("✏️ Edit Recipe" if is_edit else "➕ New Recipe")
    if is_edit and st.button("← Cancel"):
        st.session_state.edit_recipe_id = None
        st.rerun()

    categories = get_categories()
    cat_names = [c[1] for c in categories]
    cat_map = {c[1]: c[0] for c in categories}

    # ── ALL inputs are outside any form — Enter key NEVER saves accidentally ──
    name   = st.text_input("Recipe Name *", value=prefill["name"],   placeholder="e.g. Grandma's Risotto", key="form_name")
    author = st.text_input("Added by",      value=prefill["author"], placeholder="Your name or Kelia",      key="form_author")

    col_cat, col_new = st.columns([3, 2])
    with col_cat:
        sel_cat = st.selectbox("Category", cat_names,
                               index=cat_names.index(prefill["category"]) if prefill["category"] in cat_names else 0,
                               key="form_sel_cat")
    with col_new:
        new_cat = st.text_input("Or create new category", placeholder="e.g. 🫕 Stews", key="form_new_cat")

    col_s, col_p, col_c = st.columns(3)
    with col_s: servings = st.number_input("Servings",   1,   20, value=prefill["servings"], key="form_servings")
    with col_p: prep     = st.number_input("Prep (min)", 0,  600, value=prefill["prep"],     key="form_prep")
    with col_c: cook     = st.number_input("Cook (min)", 0,  600, value=prefill["cook"],     key="form_cook")

    uploaded = st.file_uploader("📷 Photo (optional)", type=["jpg", "jpeg", "png"], key="form_photo")
    notes    = st.text_area("📝 Notes / Tips", value=prefill["notes"],
                            placeholder="Any extra tips, substitutions…", height=80, key="form_notes")

    # ── Ingredients ──
    st.markdown("### 🛒 Ingredients")
    n_ing = st.session_state.ingredient_count
    default_ings = prefill["ingredients"] + [("", "", "")] * max(0, n_ing - len(prefill["ingredients"]))

    ing_rows = []
    for i in range(n_ing):
        ca, cb, cc = st.columns([4, 2, 2])
        dname = default_ings[i][0] if i < len(default_ings) else ""
        dqty  = default_ings[i][1] if i < len(default_ings) else ""
        dunit = default_ings[i][2] if i < len(default_ings) else ""
        with ca: iname = st.text_input(f"Ingredient {i+1}", value=dname, key=f"iname_{i}", label_visibility="collapsed", placeholder=f"Ingredient {i+1}")
        with cb: iqty  = st.text_input("Qty",  value=dqty,  key=f"iqty_{i}",  label_visibility="collapsed", placeholder="Qty")
        with cc: iunit = st.text_input("Unit", value=dunit, key=f"iunit_{i}", label_visibility="collapsed", placeholder="Unit")
        ing_rows.append((iname, iqty, iunit))

    c1, c2 = st.columns(2)
    with c1:
        if st.button("+ Add Ingredient Row", key="add_ing_row"):
            st.session_state.ingredient_count += 1
            st.rerun()

    # ── Steps ──
    st.markdown("### 👨‍🍳 Steps")
    n_step = st.session_state.step_count
    default_steps = prefill["steps"] + [""] * max(0, n_step - len(prefill["steps"]))

    step_rows = []
    for i in range(n_step):
        dst = default_steps[i] if i < len(default_steps) else ""
        step_text = st.text_area(f"Step {i+1}", value=dst, key=f"step_{i}", height=68, placeholder=f"Describe step {i+1}…")
        step_rows.append(step_text)

    with c2:
        if st.button("+ Add Step Row", key="add_step_row"):
            st.session_state.step_count += 1
            st.rerun()

    st.divider()
    # ── THE ONLY WAY to save — a plain button, not inside any form ──
    submitted = st.button("💾 Save Recipe", type="primary", use_container_width=True, key="save_recipe_btn")

    if submitted:
        # Read all values from session_state (no form wrapper, so widgets store into ss by key)
        name     = st.session_state.get("form_name",     "").strip()
        author   = st.session_state.get("form_author",   "").strip()
        new_cat  = st.session_state.get("form_new_cat",  "").strip()
        sel_cat  = st.session_state.get("form_sel_cat",  cat_names[0] if cat_names else "")
        servings = st.session_state.get("form_servings", 2)
        prep     = st.session_state.get("form_prep",     0)
        cook     = st.session_state.get("form_cook",     0)
        notes    = st.session_state.get("form_notes",    "").strip()

        if not name:
            st.error("⚠️ Recipe name is required!")
            return

        # Handle new category
        final_cat_name = new_cat if new_cat else sel_cat
        if new_cat:
            execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (final_cat_name,))
        cat_id = fetch_all("SELECT category_id FROM categories WHERE name = ?", (final_cat_name,))
        cat_id = cat_id[0][0] if cat_id else None

        # Image — read from the uploaded widget (file_uploader value is in local var)
        image_blob = None
        if uploaded:
            img = Image.open(uploaded).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=80)
            image_blob = buf.getvalue()

        # Read ingredient rows from session_state by key
        ing_rows = []
        for i in range(st.session_state.ingredient_count):
            iname = st.session_state.get(f"iname_{i}", "").strip()
            iqty  = st.session_state.get(f"iqty_{i}",  "").strip()
            iunit = st.session_state.get(f"iunit_{i}", "").strip()
            ing_rows.append((iname, iqty, iunit))

        # Read step rows from session_state by key
        step_rows = []
        for i in range(st.session_state.step_count):
            step_rows.append(st.session_state.get(f"step_{i}", "").strip())

        if is_edit:
            execute("""UPDATE recipes SET name=?, category_id=?, servings=?, prep_min=?,
                       cook_min=?, notes=?, author=? WHERE recipe_id=?""",
                    (name, cat_id, servings, prep, cook, notes, author, edit_id))
            if image_blob:
                execute("UPDATE recipes SET image=? WHERE recipe_id=?", (image_blob, edit_id))
            execute("DELETE FROM ingredients WHERE recipe_id=?", (edit_id,))
            execute("DELETE FROM steps WHERE recipe_id=?", (edit_id,))
            recipe_id = edit_id
        else:
            recipe_id = execute(
                "INSERT INTO recipes (name, category_id, servings, prep_min, cook_min, notes, author, image) VALUES (?,?,?,?,?,?,?,?)",
                (name, cat_id, servings, prep, cook, notes, author, image_blob)
            )

        # Save ingredients
        for iname, iqty, iunit in ing_rows:
            if iname:
                execute("INSERT INTO ingredients (recipe_id, name, qty, unit) VALUES (?,?,?,?)",
                        (recipe_id, iname, iqty, iunit))

        # Save steps
        for idx, stext in enumerate(step_rows, 1):
            if stext:
                execute("INSERT INTO steps (recipe_id, step_number, instruction) VALUES (?,?,?)",
                        (recipe_id, idx, stext))

        # Reset form state
        for key in ["form_name", "form_author", "form_new_cat", "form_notes"]:
            st.session_state.pop(key, None)
        for i in range(st.session_state.ingredient_count):
            for prefix in ["iname_", "iqty_", "iunit_"]:
                st.session_state.pop(f"{prefix}{i}", None)
        for i in range(st.session_state.step_count):
            st.session_state.pop(f"step_{i}", None)
        st.session_state.ingredient_count = 3
        st.session_state.step_count = 3
        st.session_state.edit_recipe_id = None

        st.success(f"✅ Recipe **{name}** saved!")
        st.balloons()
        st.rerun()


# ─────────────────────────────────────────
#  RECIPE CARDS
# ─────────────────────────────────────────

def show_recipe_cards(recipes):
    if not recipes:
        st.markdown('<div class="empty-state"><span class="emoji">🍽️</span>No recipes here yet.<br>Add your first one!</div>', unsafe_allow_html=True)
        return

    for row in recipes:
        rid, rname, rcat, rservings, rprep, rcook, rfav, rauthor, rimage = row
        total_time = rprep + rcook
        fav_icon = "❤️" if rfav else ""

        col_img, col_info = st.columns([1, 3]) if rimage else [None, None]

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
                if st.button("Open →", key=f"open_{rid}"):
                    st.session_state.view_recipe_id = rid
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────
#  ROUTING
# ─────────────────────────────────────────

# Detail view
if st.session_state.view_recipe_id:
    show_detail(st.session_state.view_recipe_id)

# Edit form
elif st.session_state.edit_recipe_id:
    show_recipe_form(edit_id=st.session_state.edit_recipe_id)

# Main tabs
else:
    tab_browse, tab_add, tab_favs = st.tabs(["🏠 Browse", "➕ Add Recipe", "❤️ Favourites"])

    # ── BROWSE TAB ──
    with tab_browse:
        search = st.text_input("🔍 Search recipes…", placeholder="e.g. pasta, risotto…", label_visibility="collapsed")

        categories = get_categories()
        cat_names = ["All"] + [c[1] for c in categories]
        cat_map = {c[1]: c[0] for c in categories}
        sel_filter = st.selectbox("Filter by category", cat_names, label_visibility="collapsed")
        filter_cat_id = cat_map.get(sel_filter) if sel_filter != "All" else None

        recipes = get_recipes(favourite_only=False, category_id=filter_cat_id, search=search)
        total = len(recipes)
        st.caption(f"{total} recipe{'s' if total != 1 else ''} found")
        show_recipe_cards(recipes)

    # ── ADD TAB ──
    with tab_add:
        show_recipe_form()

    # ── FAVOURITES TAB ──
    with tab_favs:
        fav_recipes = get_recipes(favourite_only=True)
        if not fav_recipes:
            st.markdown('<div class="empty-state"><span class="emoji">❤️</span>No favourites yet.<br>Open a recipe and tap ❤️ Favourite.</div>', unsafe_allow_html=True)
        else:
            show_recipe_cards(fav_recipes)
