import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import plotly.graph_objects as go

# --- 1. GLOBAL CONFIGURATION & LICENSE ---
VALID_KEY = "EDU-PRO-200"
st.set_page_config(page_title="Edu-Supply Chain Master", layout="wide")

# Initialize session states for data persistence
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'main_capital' not in st.session_state:
    st.session_state['main_capital'] = 0.0
if 'sector_data' not in st.session_state:
    st.session_state['sector_data'] = {
        "Primary": {"spent": 0.0, "profit": 100},
        "Secondary": {"spent": 0.0, "profit": 100},
        "College": {"spent": 0.0, "profit": 100}
    }

# --- 2. PDF ENGINE CLASS ---
class PDF_Report(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'INVENTORY & SUPPLY CHAIN STRATEGIC REPORT', 0, 1, 'C')
        self.ln(5)

def create_pdf_report(inst_name, title, details, score, remaining_cap):
    pdf = PDF_Report()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Institute: {inst_name}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Report Type: {title} | Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.line(10, 45, 200, 45)
    pdf.ln(10)
    
    for key, val in details.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(50, 10, f"{key}: ", ln=0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 10, f"{val}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"STRATEGIC PROFIT SCORE: {score}/200", ln=True)
    pdf.cell(0, 10, f"REMAINING GLOBAL CAPITAL: {remaining_cap}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ACTIVATION SCREEN ---
if not st.session_state['auth']:
    st.title("🔐 Software Activation & Registration")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Enter Institute/School Name")
        key = st.text_input("Enter 1-Year License Key", type="password")
        initial_cap = st.number_input("Enter Initial Main Capital Budget", min_value=0.0, value=1000000.0)
        
        if st.button("Activate & Initialize"):
            if key == VALID_KEY:
                st.session_state['auth'] = True
                st.session_state['inst_name'] = name
                st.session_state['main_capital'] = initial_cap
                st.rerun()
            else:
                st.error("Invalid License Key!")
    st.stop()

# --- 4. MAIN INTERFACE ---
st.sidebar.title(f"🏢 {st.session_state['inst_name']}")
st.sidebar.subheader(f"Total Capital: {st.session_state['main_capital']:,.2f}")

# Calculate remaining capital
total_spent = sum(item['spent'] for item in st.session_state['sector_data'].values())
remaining_capital = st.session_state['main_capital'] - total_spent

st.sidebar.markdown(f"**💰 Remaining Capital:** \n### {remaining_capital:,.2f}")

sector_choice = st.sidebar.selectbox("Select Education Sector", ["Primary", "Secondary", "College"])
logic_page = st.sidebar.radio("Optimization Logic", [
    "Dashboard & Summary", 
    "1. Capital & Resource Logic", 
    "2. Quotation & Market Selection", 
    "3. Build vs Buy (Manufacturing)", 
    "4. Inventory Risk & Timing"
])

# --- DASHBOARD & GLOBAL SUMMARY ---
if logic_page == "Dashboard & Summary":
    st.title("📊 Global Decision Dashboard")
    
    cols = st.columns(3)
    for i, (s_name, s_data) in enumerate(st.session_state['sector_data'].items()):
        with cols[i]:
            st.metric(f"{s_name} Profit Level", f"{s_data['profit']}/200")
            st.write(f"Spent: {s_data['spent']:,.0f}")
            
    # Comparative Profit Chart
    fig = go.Figure(data=[
        go.Bar(name='Profit Score', x=list(st.session_state['sector_data'].keys()), 
               y=[d['profit'] for d in st.session_state['sector_data'].values()], marker_color='teal')
    ])
    fig.update_layout(title="Cross-Sector Profit Level Comparison", yaxis_range=[0, 200])
    st.plotly_chart(fig)
    
    if st.button("Download Master Strategic Report (PDF)"):
        details = {
            "Total Initial Capital": st.session_state['main_capital'],
            "Total Spent Across Sectors": total_spent,
            "Primary Status": f"Score {st.session_state['sector_data']['Primary']['profit']}",
            "Secondary Status": f"Score {st.session_state['sector_data']['Secondary']['profit']}",
            "College Status": f"Score {st.session_state['sector_data']['College']['profit']}"
        }
        report = create_pdf_report(st.session_state['inst_name'], "Global Master Report", details, "Avg Score", remaining_capital)
        st.download_button("Click to Download Master PDF", report, "Master_Report.pdf")

# --- 1. CAPITAL ALLOCATION LOGIC ---
elif logic_page == "1. Capital & Resource Logic":
    st.header(f"💰 Capital Allocation - {sector_choice}")
    st.write(f"Current {sector_choice} Expenditure: {st.session_state['sector_data'][sector_choice]['spent']:,.2f}")
    
    new_expense = st.number_input("Add New Resource/Asset Expense", min_value=0.0)
    expense_cat = st.selectbox("Category", ["Infrastructure", "Staffing", "Technology", "Furniture"])
    
    if st.button("Allocate Funds"):
        if new_expense <= remaining_capital:
            st.session_state['sector_data'][sector_choice]['spent'] += new_expense
            st.success("Capital Allocated Successfully!")
            st.rerun()
        else:
            st.error("Insufficient Global Capital!")

# --- 2. QUOTATION & MARKET SELECTION ---
elif logic_page == "2. Quotation & Market Selection":
    st.header(f"⚖️ Market Analyzer & Quotation Selection - {sector_choice}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        item_name = st.text_input("Item Name (e.g. Tablets, Books)")
        market_benchmark = st.number_input("Market Average Price", value=100.0)
    with col_b:
        vendor_price = st.number_input("Vendor Quoted Price", value=90.0)
        quality_rating = st.slider("Quality Rating (1-10)", 1, 10, 7)

    # Smart Logic
    savings = market_benchmark - vendor_price
    efficiency_score = (quality_rating * 10) + (savings / market_benchmark * 100)
    
    if st.button("Analyze Quotation"):
        if vendor_price < market_benchmark and quality_rating >= 7:
            st.success(f"✅ RECOMMENDED: This purchase saves {savings} and meets quality standards.")
            st.session_state['sector_data'][sector_choice]['profit'] = min(200, st.session_state['sector_data'][sector_choice]['profit'] + 10)
        else:
            st.warning("⚠️ CRITICAL: Quotation is either overpriced or quality is too low.")
            st.session_state['sector_data'][sector_choice]['profit'] = max(1, st.session_state['sector_data'][sector_choice]['profit'] - 15)

# --- 3. BUILD VS BUY ---
elif logic_page == "3. Build vs Buy (Manufacturing)":
    st.header(f"🛠️ Manufacturing Decision - {sector_choice}")
    st.write("Determine if the school should build items (like furniture) or buy ready-made.")
    
    in_house = st.number_input("Internal Production Cost (Labor + Material)", value=5000)
    market_ready = st.number_input("Market Ready-made Price", value=7000)
    
    if in_house < market_ready:
        diff = market_ready - in_house
        st.success(f"PROFIT ALERT: Building in-house saves {diff} per unit. Score increased!")
    else:
        st.error("LOSS ALERT: Market price is cheaper. Do not build in-house.")

# --- 4. INVENTORY RISK ---
elif logic_page == "4. Inventory Risk & Timing":
    st.header(f"📦 Inventory Timing & Risk - {sector_choice}")
    risk_level = st.select_slider("Current Market Inflation Risk", options=["Low", "Stable", "Rising", "High"])
    
    if risk_level in ["Rising", "High"]:
        st.warning("Decision: Strategic Pre-buying recommended to lock current prices.")
    else:
        st.info("Decision: Maintain Just-in-Time inventory to keep capital liquid.")
        
    if st.button(f"Print {sector_choice} Section Report"):
        details = {
            "Sector": sector_choice,
            "Total Spent": st.session_state['sector_data'][sector_choice]['spent'],
            "Current Risk Assessment": risk_level,
            "Strategy": "Optimized via Edu-Supply Chain Logic"
        }
        report = create_pdf_report(st.session_state['inst_name'], f"{sector_choice} Analysis", details, 
                                   st.session_state['sector_data'][sector_choice]['profit'], remaining_capital)
        st.download_button(f"Download {sector_choice} PDF", report, f"{sector_choice}_Report.pdf")
