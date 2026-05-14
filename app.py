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

def split_full_name(full_name):
    parts = full_name.strip().split()
    if len(parts) == 0:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    if len(parts) == 2:
        return parts[0], parts[1]
    if len(parts) == 3:
        return f"{parts[0]} {parts[1]}", parts[2]
    return f"{parts[0]} {parts[1]}", parts[-1]

st.set_page_config(
    page_title="🌍Name Origin Search",
    page_icon="🌍",
    layout="centered"
)

st.markdown("""
<script>
document.addEventListener("keydown", function(e) {
    const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
    const focused = document.activeElement;
    const idx = inputs.indexOf(focused);

    if (e.key === "Tab" && idx !== -1 && idx < inputs.length - 1) {
        e.preventDefault();
        inputs[idx + 1].focus();
    }

    if (e.key === "Enter" && idx !== -1) {
        const btn = document.querySelector('button[kind="primary"]');
        if (btn) btn.click();
    }
});
</script>
<style>
[data-testid="stForm"] {
    border: none;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

st.title("Name Origin Comparator")
st.caption("Paste full names to compare country of origin")

st.divider()

with st.form("name_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sender Name")
        full_name_1 = st.text_input("Full Name", placeholder="e.g. Alice Smith", label_visibility="collapsed")
    with col2:
        st.subheader("Recipient Name")
        full_name_2 = st.text_input("Full Name", placeholder="e.g. Raj Patel", label_visibility="collapsed")

    st.divider()
    submitted = st.form_submit_button("🔍 Compare Origin", use_container_width=True)

if submitted:
    fn1, ln1 = split_full_name(full_name_1)
    fn2, ln2 = split_full_name(full_name_2)

    if not fn1 or not fn2:
        st.error("Please enter at least a first name for both people.")
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
        region1 = data[0].get("regionOrigin", "—")
        region2 = data[1].get("regionOrigin", "—")

        if c1 == c2:
            st.markdown("### Same country of origin")
        else:
            st.markdown("### Different countries of origin")

        table_data = {
            "Name": [full_name_1, full_name_2],
            "Country of Origin": [name1, name2],
            "Region": [region1, region2],
        }
        st.table(table_data)

    except Exception as e:
        st.error(f"API Error: {e}")
