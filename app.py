import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SYSTEM CONFIGURATION ---
VALID_LICENSE = "Ahsan123"
st.set_page_config(page_title="Inventory-and-Supply-Chain-Management-Optimization", layout="wide")

# Persistent State Management
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'main_capital' not in st.session_state:
    st.session_state['main_capital'] = 0.0
if 'capital_locked' not in st.session_state:
    st.session_state['capital_locked'] = False
if 'project_data' not in st.session_state:
    sectors = ["Primary", "Secondary", "College"]
    st.session_state['project_data'] = {s: {"spent": 0.0, "profit": 100, "records": []} for s in sectors}

# --- 2. AUTHENTICATION ---
if not st.session_state['auth']:
    st.title("🔐 Inventory-and-Supply-Chain-Management-Optimization")
    inst_name = st.text_input("Institute Name")
    key = st.text_input("Strategic License Key", type="password")
    if st.button("Unlock System"):
        if key == VALID_LICENSE:
            st.session_state['auth'] = True
            st.session_state['inst_name'] = inst_name
            st.rerun()
        else: st.error("Access Denied: Invalid Key")
    st.stop()

# --- 3. GLOBAL MONITORING & SYSTEM CONTROLS ---
total_spent = sum(s['spent'] for s in st.session_state['project_data'].values())
remaining_balance = st.session_state['main_capital'] - total_spent

st.sidebar.title(f"🏢 {st.session_state['inst_name']}")

# NEW: System Controls Section
st.sidebar.markdown("### ⚙️ System Controls")
col1, col2 = st.sidebar.columns(2)

# Log Out Logic
if col2.button("Log Out"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Save Logic (Google Sheets Integration)
if col1.button("Save Data"):
    try:
        # Create connection (Uses secrets.toml or Streamlit Cloud Secrets)
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Flatten data for Google Sheets
        all_records = []
        for sector, content in st.session_state['project_data'].items():
            for rec in content['records']:
                rec_copy = rec.copy()
                rec_copy['Sector'] = sector
                rec_copy['Institute'] = st.session_state['inst_name'] # Project Identification
                all_records.append(rec_copy)
        
        if all_records:
            df_to_save = pd.DataFrame(all_records)
            # Identifies the app by using the Institute Name as the worksheet name
            conn.update(worksheet=st.session_state['inst_name'], data=df_to_save)
            st.sidebar.success("Data Synced to Cloud!")
        else:
            st.sidebar.warning("No data to save.")
    except Exception as e:
        st.sidebar.error(f"Cloud Save Failed: {e}")

if st.session_state['capital_locked']:
    st.sidebar.markdown("---")
    st.sidebar.metric("Available Capital", f"{remaining_balance:,.2f}")
    st.sidebar.progress(max(0.0, min(1.0, remaining_balance/st.session_state['main_capital'])))

# Backup functionality
with st.sidebar.expander("💾 Local Backup"):
    st.download_button("Export JSON", json.dumps(st.session_state['project_data']), "data.json")

nav = st.sidebar.radio("Optimization Logic", ["Global Dashboard", "1. Capital & Resources", "2. Market Selection", "3. Build vs Buy", "4. Inventory Risk"])
active_sector = st.sidebar.selectbox("Active Sector", ["Primary", "Secondary", "College"])

# --- 4. DASHBOARD & COMPARATIVE ANALYZER ---
if nav == "Global Dashboard":
    st.title("📊 Master Strategic Dashboard")
    
    if not st.session_state['capital_locked']:
        st.warning("Initialize system with Fixed Capital.")
        cap_in = st.number_input("Enter Total Budget", min_value=1.0, value=1000000.0)
        if st.button("Lock Capital & Begin"):
            st.session_state['main_capital'] = cap_in
            st.session_state['capital_locked'] = True
            st.rerun()
    else:
        st.subheader("⚠️ Sector-Wise Gap Analysis")
        scores = {k: v['profit'] for k, v in st.session_state['project_data'].items()}
        weakest = min(scores, key=scores.get)
        
        c1, c2, c3 = st.columns(3)
        for i, (name, val) in enumerate(st.session_state['project_data'].items()):
            with [c1, c2, c3][i]:
                st.info(f"**{name} Sector**")
                st.metric("Profit Score", f"{val['profit']}/200")
                if name == weakest and val['profit'] < 140:
                    st.error(f"High Priority: {name} needs urgent optimization.")
                elif val['spent'] < (st.session_state['main_capital'] * 0.1):
                    st.warning(f"Low funding detected in {name}.")
                else:
                    st.success(f"{name} is performing well.")

# --- 5. STRATEGIC PILLAR MODULES ---
else:
    st.title(f"🛠️ {nav}")
    st.write(f"Remaining Global Funds: **{remaining_balance:,.2f}**")

    with st.form("pillar_form"):
        st.subheader("Strategic Decisions (Dropdowns)")
        if "Capital" in nav:
            decision = st.selectbox("Allocation Type?", ["Infrastructure (High Impact)", "Social Resources (Medium Impact)", "Basic Maintenance (Low Impact)"])
        elif "Market" in nav:
            decision = st.selectbox("Quotation Status?", ["Vendor cheaper than Market", "Market cheaper than Vendor", "Same Price"])
        elif "Build" in nav:
            decision = st.selectbox("Production Choice?", ["In-house Production (Cost-Saving)", "Outsourced (Expensive)"])
        else: # Inventory
            decision = st.selectbox("Risk Level?", ["Low (Safe Stock)", "Medium (Price Volatility)", "High (Supply Gap)"])

        st.subheader("Custom Data Entry")
        label = st.text_input("Entry Description (e.g. Lab Repair, Book Vendor)")
        cost = st.number_input("Transaction Amount", min_value=0.0)
        details = st.text_area("Analysis / Notes")

        if st.form_submit_button("Submit Strategy"):
            if cost <= remaining_balance:
                impact = 15 if ("High Impact" in decision or "cheaper" in decision or "Saving" in decision or "Low" in decision) else -10
                
                new_rec = {"Pillar": nav, "Label": label, "Cost": cost, "Impact": decision, "Time": datetime.now().strftime("%Y-%m-%d")}
                st.session_state['project_data'][active_sector]['records'].append(new_rec)
                st.session_state['project_data'][active_sector]['spent'] += cost
                st.session_state['project_data'][active_sector]['profit'] = max(0, min(200, st.session_state['project_data'][active_sector]['profit'] + impact))
                st.rerun()
            else: st.error("Global Budget Exceeded!")

    if st.session_state['project_data'][active_sector]['records']:
        st.table(pd.DataFrame(st.session_state['project_data'][active_sector]['records']))
