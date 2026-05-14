import streamlit as st
import requests
import pycountry

# ---------------- CONFIG ----------------
API_URL = "https://v2.namsor.com/NamSorAPIv2/api2/json/originBatch"
# ----------------------------------------

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
    page_title="Name Origin Search",
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

# ── API Key Gate ──────────────────────────────────────────────
if "namsor_api_key" not in st.session_state:
    st.title("Name Origin Search 🌍")
    st.divider()
    st.subheader("Enter your NamSor API Key to continue")
    st.markdown(
        "You can get a free API key at [namsor.com](https://namsor.com). "
        "Your key is used only for this session and is never stored."
    )
    with st.form("api_key_form"):
        api_key_input = st.text_input(
            "NamSor API Key",
            type="password",
            placeholder="Paste your API key here"
        )
        submitted_key = st.form_submit_button("Continue →", use_container_width=True)

    if submitted_key:
        if not api_key_input.strip():
            st.error("Please enter a valid API key.")
        else:
            st.session_state.namsor_api_key = api_key_input.strip()
            st.rerun()
    st.stop()

# ── Sidebar: allow key reset ──────────────────────────────────
with st.sidebar:
    st.markdown("**NamSor API Key**")
    st.caption("Key loaded for this session ✅")
    if st.button("🔄 Change API Key"):
        del st.session_state.namsor_api_key
        st.rerun()

API_KEY = st.session_state.namsor_api_key

# ── Main App ──────────────────────────────────────────────────
st.title("Name Origin Search")
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
        if response.status_code == 401:
            st.error("❌ Invalid API key. Please check your key and try again.")
            if st.button("Re-enter API Key"):
                del st.session_state.namsor_api_key
                st.rerun()
            st.stop()
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
