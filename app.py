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
        "Primary": {"spent": 0.0, "profit": 100, "items": []},
        "Secondary": {"spent": 0.0, "profit": 100, "items": []},
        "College": {"spent": 0.0, "profit": 100, "items": []}
    }

# --- 2. DATA SAVE/LOAD LOGIC ---
def save_data():
    data = {
        "main_capital": st.session_state['main_capital'],
        "cap_set": st.session_state['cap_set'],
        "sector_data": st.session_state['sector_data']
    }
    return json.dumps(data)

def load_data(uploaded_file):
    data = json.load(uploaded_file)
    st.session_state['main_capital'] = data['main_capital']
    st.session_state['cap_set'] = data['cap_set']
    st.session_state['sector_data'] = data['sector_data']
    st.success("Record Loaded Successfully!")

# --- 3. LOGIN SCREEN ---
if not st.session_state['auth']:
    st.title("🔐 Enterprise Login")
    inst_name = st.text_input("Institute Name")
    key = st.text_input("License Key", type="password")
    if st.button("Access System"):
        if key == VALID_KEY:
            st.session_state['auth'] = True
            st.session_state['inst_name'] = inst_name
            st.rerun()
        else: st.error("Access Denied!")
    st.stop()

# --- 4. SIDEBAR & NAVIGATION ---
total_spent = sum(s['spent'] for s in st.session_state['sector_data'].values())
remaining_cap = st.session_state['main_capital'] - total_spent

st.sidebar.title(f"🏢 {st.session_state['inst_name']}")
if st.session_state['cap_set']:
    st.sidebar.metric("Available Capital", f"{remaining_cap:,.0f}")

# Save/Load in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Backup Record")
st.sidebar.download_button("Download Work to PC", save_data(), "school_data.json")
uploaded_file = st.sidebar.file_uploader("Upload Previous Work", type="json")
if uploaded_file:
    if st.sidebar.button("Restore Now"):
        load_data(uploaded_file)
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state['auth'] = False
    st.rerun()

sector = st.sidebar.selectbox("Sector", ["Primary", "Secondary", "College"])
page = st.sidebar.radio("Navigate", ["Summary Dashboard", "Capital Logic", "Quotation Analyzer"])

# --- 5. DASHBOARD & FIXED CAPITAL SETUP ---
if page == "Summary Dashboard":
    st.title("📊 Master Dashboard")
    
    if not st.session_state['cap_set']:
        st.warning("First, please set your FIXED Total Capital Budget.")
        init_cap = st.number_input("Enter Total Budget Amount", min_value=1.0)
        if st.button("Set & Lock Capital"):
            st.session_state['main_capital'] = init_cap
            st.session_state['cap_set'] = True
            st.rerun()
    else:
        st.success(f"Capital Locked: {st.session_state['main_capital']:,.0f}")
        col1, col2 = st.columns(2)
        col1.metric("Current Profit Score", f"{sum(s['profit'] for s in st.session_state['sector_data'].values())/3:.0f}/200")
        col2.metric("Remaining Budget", f"{remaining_cap:,.0f}")
        
        # summary table
        df = pd.DataFrame.from_dict(st.session_state['sector_data'], orient='index')
        st.table(df[['spent', 'profit']])

# --- 6. CAPITAL LOGIC ---
elif page == "Capital Logic":
    st.header(f"💰 Allocation - {sector}")
    with st.expander("➕ Add Custom Expense/Item"):
        name = st.text_input("Item Name")
        cost = st.number_input("Cost", min_value=0.0)
        if st.button("Add Entry"):
            if cost <= remaining_cap:
                st.session_state['sector_data'][sector]['spent'] += cost
                st.session_state['sector_data'][sector]['items'].append(name)
                st.rerun()
            else: st.error("Insufficient Funds!")

# --- 7. QUOTATION ANALYZER ---
elif page == "Quotation Analyzer":
    st.header(f"⚖️ Analyze Quotation - {sector}")
    with st.expander("➕ New Market Comparison"):
        mkt = st.number_input("Market Rate", value=100.0)
        vnd = st.number_input("Vendor Rate", value=90.0)
        if st.button("Analyze"):
            if vnd < mkt:
                st.session_state['sector_data'][sector]['profit'] = min(200, st.session_state['sector_data'][sector]['profit'] + 10)
                st.success("Decision Saved: Score Improved!")
            else:
                st.session_state['sector_data'][sector]['profit'] = max(0, st.session_state['sector_data'][sector]['profit'] - 10)
                st.error("Decision Saved: Score Reduced!")
            st.rerun()
