import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
from datetime import datetime
import io

# --- 1. CORE SYSTEM CONFIGURATION ---
VALID_LICENSE = "EDU-PRO-200"
st.set_page_config(page_title="Edu-Strategic Supply Master", layout="wide")

# Initialize Session States
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'main_capital' not in st.session_state:
    st.session_state['main_capital'] = 0.0
if 'is_capital_locked' not in st.session_state:
    st.session_state['is_capital_locked'] = False
if 'institute_name' not in st.session_state:
    st.session_state['institute_name'] = ""
if 'data_store' not in st.session_state:
    # Profit Level Range: 1 to 200 (Default: 100)
    st.session_state['data_store'] = {
        "Primary": {"spent": 0.0, "profit_level": 100, "entries": []},
        "Secondary": {"spent": 0.0, "profit_level": 100, "entries": []},
        "College": {"spent": 0.0, "profit_level": 100, "entries": []}
    }

# --- 2. UTILITY FUNCTIONS ---

def generate_pdf_report(sector_name, sector_data, total_cap, remaining_cap):
    """Generates a professional Strategic PDF Report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, "Strategic Supply Chain Report", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Institute: {st.session_state['institute_name']}", ln=True)
    pdf.cell(0, 10, f"Sector: {sector_name} | Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    
    # Financial Summary Section
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " Financial Summary", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Total Fixed Project Capital: {total_cap:,.2f}", ln=True)
    pdf.cell(0, 10, f"Remaining Available Capital: {remaining_cap:,.2f}", ln=True)
    pdf.cell(0, 10, f"Sector Profit Level: {sector_data['profit_level']}/200", ln=True)
    pdf.ln(5)

    # Entry Records Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, " Detailed Decision Entries", ln=True, fill=True)
    pdf.set_font("Arial", '', 10)
    for entry in sector_data['entries']:
        record_text = f"[{entry['time']}] {entry['cat']} - {entry['name']}: Amount {entry['amount']} | Info: {entry['details']}"
        pdf.multi_cell(0, 8, record_text)
        pdf.ln(1)
    
    return pdf.output(dest='S').encode('latin-1')

def export_json_backup():
    """Bundles all state data into a JSON string for backup."""
    backup_data = {
        "main_capital": st.session_state['main_capital'],
        "locked": st.session_state['is_capital_locked'],
        "store": st.session_state['data_store'],
        "inst": st.session_state['institute_name']
    }
    return json.dumps(backup_data, indent=4)

# --- 3. AUTHENTICATION LAYER ---
if not st.session_state['authenticated']:
    st.title("🔐 Enterprise Strategic Portal")
    inst_input = st.text_input("Enter Institute Name")
    license_input = st.text_input("Enter License Key", type="password")
    
    if st.button("Activate System"):
        if license_input == VALID_LICENSE:
            st.session_state['authenticated'] = True
            st.session_state['institute_name'] = inst_input
            st.rerun()
        else:
            st.error("Invalid License Key. Access Denied.")
    st.stop()

# --- 4. SIDEBAR GLOBAL MONITORING ---
total_spent_global = sum(s['spent'] for s in st.session_state['data_store'].values())
remaining_capital_global = st.session_state['main_capital'] - total_spent_global

st.sidebar.title(f"🏢 {st.session_state['institute_name']}")

if st.session_state['is_capital_locked']:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Capital Status")
    st.sidebar.write(f"Fixed Budget: **{st.session_state['main_capital']:,.2f}**")
    st.sidebar.metric("Available Funds", f"{remaining_capital_global:,.2f}", delta_color="normal")
    
    # Capital Usage Visualizer
    usage_ratio = max(0.0, min(1.0, remaining_capital_global / st.session_state['main_capital']))
    st.sidebar.progress(usage_ratio)
    if usage_ratio < 0.2:
        st.sidebar.warning("Low Capital Warning!")

# Data Persistence (Backup/Restore)
with st.sidebar.expander("💾 System Backup"):
    st.download_button("Download Database", export_json_backup(), "strategy_backup.json")
    uploaded_file = st.file_uploader("Restore Database", type="json")
    if uploaded_file and st.button("Restore Now"):
        restored = json.load(uploaded_file)
        st.session_state['main_capital'] = restored['main_capital']
        st.session_state['is_capital_locked'] = restored['locked']
        st.session_state['data_store'] = restored['store']
        st.session_state['institute_name'] = restored['inst']
        st.rerun()

if st.sidebar.button("🚪 Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

# --- 5. NAVIGATION ---
selected_sector = st.sidebar.selectbox("Active Sector", ["Primary", "Secondary", "College"])
logic_page = st.sidebar.radio("Decision Framework", [
    "Global Dashboard", 
    "1. Capital & Resources", 
    "2. Market Selection", 
    "3. Build vs Buy", 
    "4. Inventory Risk"
])

# --- 6. DASHBOARD & GAP ANALYSIS ---
if logic_page == "Global Dashboard":
    st.title("📊 Strategic Dashboard & Gap Analysis")
    
    if not st.session_state['is_capital_locked']:
        st.info("Welcome. Please initialize the system by setting the Total Fixed Capital.")
        initial_cap = st.number_input("Enter Total Project Budget", min_value=0.0, step=1000.0)
        if st.button("Initialize and Lock Budget"):
            st.session_state['main_capital'] = initial_cap
            st.session_state['is_capital_locked'] = True
            st.rerun()
    else:
        avg_profit_global = sum(s['profit_level'] for s in st.session_state['data_store'].values()) / 3
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Profit Level", f"{avg_profit_global:.1f}/200")
        col2.metric("Funds Remaining", f"{remaining_capital_global:,.0f}")
        col3.metric("Total Sectors", "3")

        st.markdown("---")
        st.subheader("⚠️ Gap Analysis & Strategic Needs")
        
        g1, g2, g3 = st.columns(3)
        sectors = list(st.session_state['data_store'].keys())
        for i, col in enumerate([g1, g2, g3]):
            s_name = sectors[i]
            s_val = st.session_state['data_store'][s_name]
            with col:
                st.markdown(f"#### {s_name}")
                if s_val['profit_level'] < 110:
                    st.error(f"Low Performance: Level {s_val['profit_level']}. Review procurement strategy.")
                elif s_val['profit_level'] > 170:
                    st.success("Optimal Performance. Strategy is efficient.")
                else:
                    st.warning("Average Performance. Needs market optimization.")
                
                if s_val['spent'] > (st.session_state['main_capital'] / 3):
                    st.info("High consumption of global funds.")

# --- 7. DYNAMIC MODULE LOGIC ---
else:
    st.title(f"🛠️ {logic_page}")
    st.subheader(f"Sector: {selected_sector}")
    
    # Input Framework
    with st.expander(f"➕ Add Entry to {logic_page}"):
        ca, cb = st.columns(2)
        with ca:
            item_name = st.text_input("Item Name / Strategic Action")
            item_amount = st.number_input("Transaction Amount", min_value=0.0)
        with cb:
            item_details = st.text_area("Analysis / Vendor Details / Risk Factors")
        
        if st.button("Submit Decision"):
            if item_amount <= remaining_capital_global:
                new_entry = {
                    "cat": logic_page,
                    "name": item_name,
                    "amount": item_amount,
                    "details": item_details,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state['data_store'][selected_sector]['entries'].append(new_entry)
                st.session_state['data_store'][selected_sector]['spent'] += item_amount
                
                # Logic to adjust Profit Level based on strategic module
                if "Market" in logic_page or "Build" in logic_page:
                    st.session_state['data_store'][selected_sector]['profit_level'] = min(200, st.session_state['data_store'][selected_sector]['profit_level'] + 10)
                
                st.success("Entry recorded successfully.")
                st.rerun()
            else:
                st.error("Insufficient Global Capital available for this action.")

    st.markdown("---")
    st.subheader("Stored Records")
    if st.session_state['data_store'][selected_sector]['entries']:
        all_data = pd.DataFrame(st.session_state['data_store'][selected_sector]['entries'])
        # Filter data for the current active module
        filtered_data = all_data[all_data['cat'] == logic_page]
        st.table(filtered_data)
        
        # PDF Generator Button
        if st.button(f"Generate {selected_sector} PDF Report"):
            report_bytes = generate_pdf_report(selected_sector, st.session_state['data_store'][selected_sector], st.session_state['main_capital'], remaining_capital_global)
            st.download_button(f"Download {selected_sector} Strategy.pdf", report_bytes, f"{selected_sector}_Report.pdf")
    else:
        st.info("No records found in this category.")
