import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import plotly.graph_objects as go

# --- 1. CONFIGURATION & LICENSE ---
VALID_KEY = "EDU-PRO-200"
st.set_page_config(page_title="Edu-Supply Decision Master", layout="wide")

# Session State Initialization
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'main_capital' not in st.session_state:
    st.session_state['main_capital'] = 0.0
if 'sector_data' not in st.session_state:
    st.session_state['sector_data'] = {
        "Primary": {"spent": 0.0, "profit": 100, "items": []},
        "Secondary": {"spent": 0.0, "profit": 100, "items": []},
        "College": {"spent": 0.0, "profit": 100, "items": []}
    }

# --- 2. LOGOUT FUNCTION ---
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 3. PDF REPORT ENGINE ---
def create_pdf(inst_name, title, details, score, remaining):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"{inst_name}", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    for k, v in details.items():
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"{k}: {v}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Strategic Profit Score: {score}/200", ln=True)
    pdf.cell(0, 10, f"Remaining Capital: {remaining}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. ONE-TIME ACTIVATION & FIXED CAPITAL ---
if not st.session_state['auth']:
    st.title("🔐 Enterprise Activation")
    st.info("Note: Capital entered here will be fixed and cannot be changed later.")
    inst_name = st.text_input("Enter Institute Name")
    license_key = st.text_input("Enter License Key", type="password")
    fixed_cap = st.number_input("Enter FIXED Main Capital Budget", min_value=1.0, value=1000000.0)
    
    if st.button("Activate & Lock Capital"):
        if license_key == VALID_KEY:
            st.session_state['auth'] = True
            st.session_state['inst_name'] = inst_name
            st.session_state['main_capital'] = fixed_cap
            st.rerun()
        else:
            st.error("Invalid License Key!")
    st.stop()

# --- 5. CALCULATIONS ---
total_spent = sum(s['spent'] for s in st.session_state['sector_data'].values())
remaining_capital = st.session_state['main_capital'] - total_spent
global_profit = sum(s['profit'] for s in st.session_state['sector_data'].values()) / 3

# --- 6. SIDEBAR NAVIGATION ---
st.sidebar.title(f"🏢 {st.session_state['inst_name']}")
st.sidebar.subheader(f"FIXED Capital: {st.session_state['main_capital']:,.2f}")
st.sidebar.markdown(f"**Available:** \n## {remaining_capital:,.2f}")
st.sidebar.progress(max(0.0, min(1.0, remaining_capital / st.session_state['main_capital'])))

if st.sidebar.button("🚪 Logout"):
    logout()

sector = st.sidebar.selectbox("Choose Sector", ["Primary", "Secondary", "College"])
page = st.sidebar.radio("Logic Modules", ["Summary Dashboard", "1. Capital Allocation", "2. Market Analyzer", "3. Build vs Buy", "4. Inventory Risk"])

# --- DASHBOARD ---
if page == "Summary Dashboard":
    st.title("📊 Master Strategic Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Global Profit Level", f"{global_profit:.0f}/200")
    with col2:
        st.metric("Total Investment Spent", f"{total_spent:,.2f}")
    
    # Sector Comparison Table
    df = pd.DataFrame.from_dict(st.session_state['sector_data'], orient='index')
    st.table(df[['spent', 'profit']])
    
    if st.button("Download Master PDF Report"):
        details = {"Total Capital": st.session_state['main_capital'], "Total Spent": total_spent}
        pdf_data = create_pdf(st.session_state['inst_name'], "Master Global Summary", details, global_profit, remaining_capital)
        st.download_button("Save Master PDF", pdf_data, "Master_Report.pdf")

# --- MODULE 1: CAPITAL ALLOCATION (WITH ADD OPTION) ---
elif page == "1. Capital Allocation":
    st.header(f"💰 Capital Logic - {sector}")
    st.write(f"Remaining Global Pool: {remaining_capital:,.2f}")
    
    with st.expander("➕ Add New Resource Entry"):
        res_name = st.text_input("Resource Name")
        res_cost = st.number_input("Estimated Cost", min_value=0.0)
        if st.button("Add & Allocate"):
            if res_cost <= remaining_capital:
                st.session_state['sector_data'][sector]['spent'] += res_cost
                st.session_state['sector_data'][sector]['items'].append(res_name)
                st.success(f"{res_name} added to {sector}")
                st.rerun()
            else: st.error("Not enough capital!")

# --- MODULE 2: MARKET ANALYZER (QUOTATIONS) ---
elif page == "2. Market Analyzer":
    st.header(f"⚖️ Quotation Analyzer - {sector}")
    with st.expander("➕ Add New Quotation for Comparison"):
        item = st.text_input("Item for Purchase")
        mkt_rate = st.number_input("Market Average Rate", value=100.0)
        vnd_rate = st.number_input("Vendor Quoted Rate", value=90.0)
        if st.button("Compare & Decide"):
            if vnd_rate < mkt_rate:
                st.session_state['sector_data'][sector]['profit'] = min(200, st.session_state['sector_data'][sector]['profit'] + 15)
                st.success("Strategic Buy! Profit Score Increased.")
            else:
                st.session_state['sector_data'][sector]['profit'] = max(0, st.session_state['sector_data'][sector]['profit'] - 10)
                st.error("Overpriced! Profit Score Decreased.")
            st.rerun()

# --- MODULE 3 & 4 (LOGIC INHERITED) ---
elif page == "3. Build vs Buy":
    st.header(f"🛠️ Build vs Buy - {sector}")
    # User can add custom manufacturing entries here
    st.info("Logic: Compares in-house labor+material vs Market ready-made prices.")

elif page == "4. Inventory Risk":
    st.header(f"📦 Inventory & Timing - {sector}")
    st.write("Decision support based on market inflation and capital availability.")
    if st.button(f"Print {sector} Report"):
        details = {"Sector": sector, "Spent": st.session_state['sector_data'][sector]['spent']}
        pdf_data = create_pdf(st.session_state['inst_name'], f"{sector} Unit Report", details, st.session_state['sector_data'][sector]['profit'], remaining_capital)
        st.download_button("Save PDF", pdf_data, f"{sector}_Report.pdf")
