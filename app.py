import streamlit as st
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import required modules
from database.connection import db_manager
from utils.auth import get_current_user, require_auth
from pages.login import login_page
from pages.dashboard import dashboard_page

# Configure Streamlit page
st.set_page_config(
    page_title="Data Retrieval System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_system():
    """Initialize the data retrieval system"""
    try:
        # Create database tables
        db_manager.create_tables()
        
        # Create default super admin user if it doesn't exist
        from utils.auth import create_user
        from database.models import User
        from database.connection import get_db
        
        db = next(get_db())
        try:
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                success, message = create_user(
                    username="admin",
                    password="admin123",
                    full_name="System Administrator",
                    email="admin@system.local",
                    role="super_admin"
                )
                if success:
                    st.success("Default admin user created successfully!")
                else:
                    st.warning(f"Could not create admin user: {message}")
        finally:
            db.close()
        
        # Create necessary directories
        from config import Config
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
        os.makedirs(Config.SCHEMAS_DIR, exist_ok=True)
        
        return True
        
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return False

def main():
    """Main application function"""
    # Initialize system
    if not initialize_system():
        st.error("Failed to initialize system. Please check the configuration.")
        return
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        # Show login page
        login_page()
    else:
        # Show dashboard
        dashboard_page()

if __name__ == "__main__":
    main()
