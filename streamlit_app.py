import streamlit as st
import pandas as pd
st.title("⏳ LevarT EmiT - Time Travel")
st.write("The Future of tourism.")


st.sidebar.header("Select Your Package")

packages = {
    "Peasant Package": 5,
    "Quantum Query": 15,
    "Monarch Mode": 50
}

package = st.sidebar.selectbox("Package", list(packages.keys()))
minutes = st.sidebar.slider("Minutes in Timeline", 1, 2880, 60)
minutes = st.sidebar.text_input("Minutes:")

timeline = st.selectbox(
    "Choose Timeline - the favourites",
    ["Dinosaurs Era (-65'000'000)",
     "Ancient Greece (-1000)",
    "Ancient Rome (-50)",
    "Medieval Europe (1350)",
    "Industrial revolution (1800)",
    "WW2 (1940)", 
    "Personalized"]
)
if timeline=="Personalized":
    timeline = st.text_input("Enter your Timeline (year):")


identity_multiplier = 1.0
if package != "Peasant Package":
    fame = st.selectbox("Select Identity Fame Level", [1,2,3,4,5])
    identity_multiplier = 1 + (fame * 0.2)

insurance = st.checkbox("Add Insurance (200$)")
memory_reset = st.checkbox("Add possible memory reset (100$)")

base_price = packages[package] * minutes
total_price = base_price * identity_multiplier

if insurance:
    total_price += 200
if memory_reset:
    total_price += 100

st.subheader("💰 Price Calculation")
st.write(f"Base price: ${base_price:.2f}")
st.write(f"Identity multiplier: x{identity_multiplier}")
st.write(f"Total price: ${total_price:.2f}")

if st.button("Confirm Booking"):
    st.success("🚀 Booking Confirmed! Our MinuteMen will monitor your travel.")
