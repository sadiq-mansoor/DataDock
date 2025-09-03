import bcrypt
import streamlit as st
from datetime import datetime
from database.models import User
from database.connection import get_db
from utils.audit import log_action

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username, password):
    """Authenticate user login"""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if user and verify_password(password, user.password_hash):
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Log login action
            log_action(user.id, "login", {"username": username})
            
            return user
        return None
    finally:
        db.close()

def create_user(username, password, full_name, email, role, created_by=None):
    """Create new user"""
    db = next(get_db())
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists"
        
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return False, "Email already exists"
        
        # Create new user
        hashed_password = hash_password(password)
        new_user = User(
            username=username,
            password_hash=hashed_password,
            full_name=full_name,
            email=email,
            role=role,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        
        # Log user creation
        if created_by:
            log_action(created_by, "create_user", {
                "new_username": username,
                "new_role": role
            })
        
        return True, "User created successfully"
    except Exception as e:
        db.rollback()
        return False, f"Error creating user: {str(e)}"
    finally:
        db.close()

def get_current_user():
    """Get current user from session state"""
    return st.session_state.get('user')

def require_auth():
    """Require authentication - redirect to login if not authenticated"""
    if 'user' not in st.session_state:
        st.error("Please log in to access this page")
        st.stop()

def require_role(required_roles):
    """Require specific role(s) to access functionality"""
    require_auth()
    user = get_current_user()
    
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    if user.role not in required_roles:
        st.error("You don't have permission to access this functionality")
        st.stop()

def logout():
    """Logout current user"""
    if 'user' in st.session_state:
        user = st.session_state['user']
        log_action(user.id, "logout", {"username": user.username})
        del st.session_state['user']
    st.success("Logged out successfully")
    st.rerun()
