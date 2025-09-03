import streamlit as st
from utils.auth import authenticate_user, create_user
from config import Config

def login_page():
    """Login page"""
    st.title("🔐 Data Retrieval System - Login")
    
    # Check if user is already logged in
    if 'user' in st.session_state:
        st.success(f"Welcome back, {st.session_state['user'].full_name}!")
        st.info("You are already logged in. Use the sidebar to navigate.")
        return
    
    # Login form
    with st.form("login_form"):
        st.subheader("Please log in to continue")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            login_button = st.form_submit_button("Login", type="primary")
        
        with col2:
            if st.form_submit_button("Create Demo Account"):
                # Create demo user if it doesn't exist
                success, message = create_user(
                    username="demo",
                    password="demo123",
                    full_name="Demo User",
                    email="demo@example.com",
                    role="user"
                )
                if success:
                    st.success("Demo account created! Username: demo, Password: demo123")
                else:
                    st.error(f"Error creating demo account: {message}")
        
        if login_button:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user'] = user
                    st.success(f"Welcome, {user.full_name}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")
    
    # Demo credentials info
    with st.expander("Demo Credentials"):
        st.write("""
        **Demo Account:**
        - Username: `demo`
        - Password: `demo123`
        - Role: User
        
        **Super Admin Account:**
        - Username: `admin`
        - Password: `admin123`
        - Role: Super Admin
        
        Click 'Create Demo Account' button to create the demo user if it doesn't exist.
        """)
    
    # System information
    st.markdown("---")
    st.markdown("""
    ### System Information
    - **Version:** 1.0.0
    - **Environment:** Offline/On-premise
    - **Security:** Complete offline system with audit logging
    - **Data Sources:** PostgreSQL, MySQL, CSV, JSON, XML
    """)

if __name__ == "__main__":
    login_page()
