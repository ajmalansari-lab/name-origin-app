import streamlit as st
import requests
import pycountry
import os

# ---------------- CONFIG ----------------
API_KEY = os.getenv("NAMSOR_API_KEY")
API_URL = "https://v2.namsor.com/NamSorAPIv2/api2/json/originBatch"
# ----------------------------------------

if not API_KEY:
    st.error("NAMSOR API key not found. Please set NAMSOR_API_KEY.")
    st.stop()


def country_code_to_name(code):
    country = pycountry.countries.get(alpha_2=code)
    return country.name if country else code


def country_flag(code):
    try:
        return "".join(chr(127397 + ord(c)) for c in code.upper())
    except:
        return ""


def split_full_name(full_name):
    parts = full_name.strip().split()
    if len(parts) < 2:
        return None, None
    return parts[0], parts[1]


st.set_page_config(
    page_title="Name Origin Comparator",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 Name Origin Comparator")
st.caption("Paste full names to compare country of origin")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Person 1")
    full_name_1 = st.text_input("Full Name", placeholder="e.g. Alice Smith")

with col2:
    st.subheader("Person 2")
    full_name_2 = st.text_input("Full Name", placeholder="e.g. Raj Patel")

st.divider()

if st.button("🔍 Compare Origin", use_container_width=True):

    fn1, ln1 = split_full_name(full_name_1)
    fn2, ln2 = split_full_name(full_name_2)

    if not all([fn1, ln1, fn2, ln2]):
        st.error("Please enter at least first and last name for both people.")
        st.stop()

    payload = {
        "personalNames": [
            {"id": "1", "firstName": fn1, "lastName": ln1},
            {"id": "2", "firstName": fn2, "lastName": ln2}
        ]
    }

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()["personalNames"]

        c1 = data[0]["countryOrigin"]
        c2 = data[1]["countryOrigin"]

        name1 = country_code_to_name(c1)
        name2 = country_code_to_name(c2)

        flag1 = country_flag(c1)
        flag2 = country_flag(c2)

        if c1 == c2:
            st.success("✅ Same country of origin")
        else:
            st.error("❌ Different countries of origin")

        st.markdown(f"**{full_name_1} → {flag1} {name1}**")
        st.markdown(f"**{full_name_2} → {flag2} {name2}**")

    except Exception as e:
        st.error(f"API Error: {e}")
