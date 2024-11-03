import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import hashlib
import secrets
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Modern CRM",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .auth-form {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def get_user_data_dir(username):
    """Get user-specific data directory"""
    user_dir = DATA_DIR / username
    user_dir.mkdir(exist_ok=True)
    return user_dir

def save_user_data(username, data_type, data):
    """Save user-specific data"""
    user_dir = get_user_data_dir(username)
    with open(user_dir / f"{data_type}.json", 'w') as f:
        json.dump(data, f)

def load_user_data(username, data_type):
    """Load user-specific data"""
    user_dir = get_user_data_dir(username)
    file_path = user_dir / f"{data_type}.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def auth_page():
    st.title("Welcome to Modern CRM")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        with st.form("signin_form", clear_on_submit=True):
            st.subheader("Sign In")
            username = st.text_input("Username").lower()
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                users = load_users()
                if username in users and users[username]["password"] == hash_password(password):
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.success("Successfully signed in!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("signup_form", clear_on_submit=True):
            st.subheader("Sign Up")
            new_username = st.text_input("Username").lower()
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    users = load_users()
                    if new_username in users:
                        st.error("Username already exists")
                    else:
                        users[new_username] = {
                            "password": hash_password(new_password),
                            "created_at": datetime.now().isoformat()
                        }
                        save_users(users)
                        st.success("Account created successfully! Please sign in.")

def initialize_session_data():
    """Initialize session state with user data"""
    if 'customers' not in st.session_state:
        st.session_state.customers = load_user_data(st.session_state.current_user, "customers")
    if 'deals' not in st.session_state:
        st.session_state.deals = load_user_data(st.session_state.current_user, "deals")
    if 'activities' not in st.session_state:
        st.session_state.activities = load_user_data(st.session_state.current_user, "activities")

def save_all_data():
    """Save all user data"""
    save_user_data(st.session_state.current_user, "customers", st.session_state.customers)
    save_user_data(st.session_state.current_user, "deals", st.session_state.deals)
    save_user_data(st.session_state.current_user, "activities", st.session_state.activities)

def sign_out():
    """Sign out user and clear session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# Main application logic
if not st.session_state.authenticated:
    auth_page()
else:
    # Initialize user data
    initialize_session_data()
    
    # Sidebar
    st.sidebar.title(f"Welcome, {st.session_state.current_user}")
    page = st.sidebar.radio("Go to", ["Dashboard", "Customers", "Deals", "Activities"])
    if st.sidebar.button("Sign Out"):
        sign_out()
    
    # Rest of your existing CRM code here (dashboard, customers, deals, activities functions)
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
        
        # Charts
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
                        save_all_data()
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
                        save_all_data()
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
                        save_all_data()
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
