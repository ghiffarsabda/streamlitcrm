import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Set page config
st.set_page_config(
    page_title="Modern CRM",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'customers' not in st.session_state:
    st.session_state.customers = []
if 'deals' not in st.session_state:
    st.session_state.deals = []
if 'activities' not in st.session_state:
    st.session_state.activities = []

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Customers", "Deals", "Activities"])

def save_data():
    """Save data to JSON files"""
    try:
        with open('customers.json', 'w') as f:
            json.dump(st.session_state.customers, f)
        with open('deals.json', 'w') as f:
            json.dump(st.session_state.deals, f)
        with open('activities.json', 'w') as f:
            json.dump(st.session_state.activities, f)
    except Exception as e:
        st.warning(f"Unable to save data: {e}")

def load_data():
    """Load data from JSON files"""
    try:
        if os.path.exists('customers.json'):
            with open('customers.json', 'r') as f:
                st.session_state.customers = json.load(f)
        if os.path.exists('deals.json'):
            with open('deals.json', 'r') as f:
                st.session_state.deals = json.load(f)
        if os.path.exists('activities.json'):
            with open('activities.json', 'r') as f:
                st.session_state.activities = json.load(f)
    except Exception as e:
        st.warning(f"Error loading data: {e}")

# Load data on startup
load_data()

def dashboard():
    st.title("📊 Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Customers",
            value=len(st.session_state.customers)
        )
    
    with col2:
        total_deal_value = sum(deal['value'] for deal in st.session_state.deals)
        st.metric(
            label="Total Deal Value",
            value=f"${total_deal_value:,.2f}"
        )
    
    with col3:
        open_deals = len([deal for deal in st.session_state.deals if deal['status'] == 'Open'])
        st.metric(
            label="Open Deals",
            value=open_deals
        )
    
    with col4:
        recent_activities = len([act for act in st.session_state.activities 
                               if (datetime.now() - datetime.strptime(act['date'], '%Y-%m-%d')).days <= 7])
        st.metric(
            label="Recent Activities",
            value=recent_activities
        )
    
    # Charts using native Streamlit charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Deal Pipeline")
        if st.session_state.deals:
            df_deals = pd.DataFrame(st.session_state.deals)
            deal_stats = df_deals.groupby('status')['value'].sum().reset_index()
            st.bar_chart(deal_stats.set_index('status'))
    
    with col2:
        st.subheader("Recent Activities")
        if st.session_state.activities:
            df_activities = pd.DataFrame(st.session_state.activities)
            activity_counts = df_activities['type'].value_counts()
            st.bar_chart(activity_counts)

def customers():
    st.title("👥 Customers")
    
    # Add new customer
    with st.expander("Add New Customer"):
        with st.form("new_customer"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            company = st.text_input("Company")
            phone = st.text_input("Phone")
            
            if st.form_submit_button("Add Customer"):
                if name and email:
                    st.session_state.customers.append({
                        'id': len(st.session_state.customers) + 1,
                        'name': name,
                        'email': email,
                        'company': company,
                        'phone': phone,
                        'created_date': datetime.now().strftime('%Y-%m-%d')
                    })
                    save_data()
                    st.success("Customer added successfully!")
                else:
                    st.error("Name and email are required!")
    
    # Display customers
    if st.session_state.customers:
        df = pd.DataFrame(st.session_state.customers)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No customers added yet.")

def deals():
    st.title("💰 Deals")
    
    # Add new deal
    with st.expander("Add New Deal"):
        with st.form("new_deal"):
            title = st.text_input("Deal Title")
            if st.session_state.customers:
                customer = st.selectbox(
                    "Customer",
                    options=[c['name'] for c in st.session_state.customers]
                )
            else:
                st.warning("Please add customers first")
                customer = None
            value = st.number_input("Value ($)", min_value=0.0)
            status = st.selectbox(
                "Status",
                options=["Open", "Won", "Lost", "On Hold"]
            )
            
            if st.form_submit_button("Add Deal"):
                if title and customer and value > 0:
                    st.session_state.deals.append({
                        'id': len(st.session_state.deals) + 1,
                        'title': title,
                        'customer': customer,
                        'value': value,
                        'status': status,
                        'created_date': datetime.now().strftime('%Y-%m-%d')
                    })
                    save_data()
                    st.success("Deal added successfully!")
                else:
                    st.error("Please fill in all required fields!")
    
    # Display deals
    if st.session_state.deals:
        df = pd.DataFrame(st.session_state.deals)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No deals added yet.")

def activities():
    st.title("📅 Activities")
    
    # Add new activity
    with st.expander("Add New Activity"):
        with st.form("new_activity"):
            type = st.selectbox(
                "Activity Type",
                options=["Call", "Meeting", "Email", "Task"]
            )
            if st.session_state.customers:
                customer = st.selectbox(
                    "Customer",
                    options=[c['name'] for c in st.session_state.customers]
                )
            else:
                st.warning("Please add customers first")
                customer = None
            notes = st.text_area("Notes")
            date = st.date_input("Date")
            
            if st.form_submit_button("Add Activity"):
                if notes and customer:
                    st.session_state.activities.append({
                        'id': len(st.session_state.activities) + 1,
                        'type': type,
                        'customer': customer,
                        'notes': notes,
                        'date': date.strftime('%Y-%m-%d')
                    })
                    save_data()
                    st.success("Activity added successfully!")
                else:
                    st.error("Please fill in all required fields!")
    
    # Display activities
    if st.session_state.activities:
        df = pd.DataFrame(st.session_state.activities)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No activities added yet.")

# Route to appropriate page
if page == "Dashboard":
    dashboard()
elif page == "Customers":
    customers()
elif page == "Deals":
    deals()
else:
    activities()
