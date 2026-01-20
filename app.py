import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURATION ---
VALID_KEY = "EDU-PRO-200"
st.set_page_config(page_title="Edu-Supply Chain Master", layout="wide")

# Session State Initialization
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'main_capital' not in st.session_state:
    st.session_state['main_capital'] = 0.0
if 'cap_set' not in st.session_state:
    st.session_state['cap_set'] = False
if 'sector_data' not in st.session_state:
    st.session_state['sector_data'] = {
        "Primary": {"spent": 0.0, "profit": 100, "entries": []},
        "Secondary": {"spent": 0.0, "profit": 100, "entries": []},
        "College": {"spent": 0.0, "profit": 100, "entries": []}
    }

# --- 2. BACKUP LOGIC ---
def save_data():
    return json.dumps({
        "main_capital": st.session_state['main_capital'],
        "cap_set": st.session_state['cap_set'],
        "sector_data": st.session_state['sector_data']
    })

def load_data(uploaded_file):
    data = json.load(uploaded_file)
    st.session_state['main_capital'] = data['main_capital']
    st.session_state['cap_set'] = data['cap_set']
    st.session_state['sector_data'] = data['sector_data']

# --- 3. LOGIN ---
if not st.session_state['auth']:
    st.title("🔐 Enterprise Strategic Login")
    inst = st.text_input("Institute Name")
    key = st.text_input("License Key", type="password")
    if st.button("Login"):
        if key == VALID_KEY:
            st.session_state['auth'] = True
            st.session_state['inst_name'] = inst
            st.rerun()
        else: st.error("Access Denied!")
    st.stop()

# --- 4. SIDEBAR NAVIGATION ---
total_spent = sum(s['spent'] for s in st.session_state['sector_data'].values())
remaining_cap = st.session_state['main_capital'] - total_spent

st.sidebar.title(f"🏢 {st.session_state['inst_name']}")
if st.session_state['cap_set']:
    st.sidebar.metric("Available Capital", f"{remaining_cap:,.0f}")

# Backup/Restore
with st.sidebar.expander("💾 Backup & Restore"):
    st.download_button("Download Data", save_data(), "school_record.json")
    up = st.file_uploader("Upload Data", type="json")
    if up and st.button("Restore"):
        load_data(up)
        st.rerun()

if st.sidebar.button("Logout"):
    st.session_state['auth'] = False
    st.rerun()

sector = st.sidebar.selectbox("Select Sector", ["Primary", "Secondary", "College"])
page = st.sidebar.radio("Optimization Logic", [
    "Dashboard & Summary", 
    "1. Capital & Resource Logic", 
    "2. Quotation & Market Selection", 
    "3. Build vs Buy (Manufacturing)", 
    "4. Inventory Risk & Timing"
])

# --- 5. DASHBOARD & FIXED CAPITAL ---
if page == "Dashboard & Summary":
    st.title("📊 Master Strategic Dashboard")
    if not st.session_state['cap_set']:
        st.warning("Please set the FIXED Total Capital Budget first.")
        c_val = st.number_input("Enter Budget Amount", min_value=1.0)
        if st.button("Set Capital"):
            st.session_state['main_capital'] = c_val
            st.session_state['cap_set'] = True
            st.rerun()
    else:
        st.success(f"Fixed Capital: {st.session_state['main_capital']:,.0f}")
        m1, m2 = st.columns(2)
        avg_p = sum(s['profit'] for s in st.session_state['sector_data'].values()) / 3
        m1.metric("Overall Profit Level", f"{avg_p:.0f}/200")
        m2.metric("Remaining Capital", f"{remaining_cap:,.0f}")
        
        st.subheader("Sector Wise Performance")
        df = pd.DataFrame.from_dict(st.session_state['sector_data'], orient='index')
        st.table(df[['spent', 'profit']])

# --- 6. THE FOUR MAIN HEADINGS (LOGIC MODULES) ---

elif page == "1. Capital & Resource Logic":
    st.header(f"💰 Capital Allocation - {sector}")
    with st.expander("➕ Add Resource/Capital Entry"):
        name = st.text_input("Resource Name (e.g. New Building, Lab Equipment)")
        cost = st.number_input("Cost Amount", min_value=0.0)
        if st.button("Confirm Entry"):
            if cost <= remaining_cap:
                st.session_state['sector_data'][sector]['spent'] += cost
                st.session_state['sector_data'][sector]['entries'].append(f"Res: {name} - {cost}")
                st.success("Capital Allocated and Summary Updated!")
                st.rerun()
            else: st.error("Not enough capital in global pool!")

elif page == "2. Quotation & Market Selection":
    st.header(f"⚖️ Market Selection Analyzer - {sector}")
    with st.expander("➕ Add Quotation for Comparison"):
        item = st.text_input("Item Name")
        mkt_p = st.number_input("Market Price (Benchmark)", value=100.0)
        vnd_p = st.number_input("Vendor Price", value=90.0)
        if st.button("Analyze Quotation"):
            if vnd_p < mkt_p:
                st.session_state['sector_data'][sector]['profit'] = min(200, st.session_state['sector_data'][sector]['profit'] + 15)
                st.success("Best Value Found! Profit Level Increased.")
            else:
                st.session_state['sector_data'][sector]['profit'] = max(0, st.session_state['sector_data'][sector]['profit'] - 10)
                st.error("Overpriced! Profit Level Decreased.")
            st.rerun()

elif page == "3. Build vs Buy (Manufacturing)":
    st.header(f"🛠️ Manufacturing Decision - {sector}")
    with st.expander("➕ Add Build vs Buy Analysis"):
        prod = st.text_input("Product (e.g. Desks, Uniforms)")
        make_cost = st.number_input("In-house Production Cost", value=500.0)
        buy_cost = st.number_input("Market Ready-made Price", value=700.0)
        if st.button("Save Decision"):
            if make_cost < buy_cost:
                st.session_state['sector_data'][sector]['profit'] = min(200, st.session_state['sector_data'][sector]['profit'] + 10)
                st.success(f"Strategy: Building {prod} in-house is better for capital.")
            else:
                st.session_state['sector_data'][sector]['profit'] = max(0, st.session_state['sector_data'][sector]['profit'] - 5)
                st.warning(f"Strategy: Buying {prod} from market is more efficient.")
            st.rerun()

elif page == "4. Inventory Risk & Timing":
    st.header(f"📦 Inventory Risk Logic - {sector}")
    with st.expander("➕ Add Inventory Record"):
        inv_item = st.text_input("Inventory Item")
        risk = st.selectbox("Market Risk Level", ["Low", "Stable", "Rising", "High"])
        if st.button("Save Risk Profile"):
            st.session_state['sector_data'][sector]['entries'].append(f"Inv: {inv_item} - Risk: {risk}")
            if risk in ["Rising", "High"]:
                st.warning("Advice: Pre-buy items now to avoid inflation impact on capital.")
            st.success("Inventory Profile Added.")
            st.rerun()
