import streamlit as st
from database import get_connection

st.title("⏳ ChronoVoyage")
st.write("The Future of tourism.")
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT
)
""")

conn.commit()
conn.close()
