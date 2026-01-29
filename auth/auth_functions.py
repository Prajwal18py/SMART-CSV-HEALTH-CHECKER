"""
Authentication Functions
Handles user signup, login, logout, and session management
"""
import streamlit as st
from config.supabase_config import supabase
from utils.logger import get_logger

logger = get_logger()

def sign_up(email: str, password: str, full_name: str = None):
    """
    Sign up a new user
    
    Args:
        email: User email
        password: User password
        full_name: User's full name (optional)
    
    Returns:
        dict: User data or error
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name or email.split('@')[0]
                }
            }
        })
        
        if response.user:
            logger.info(f"✅ User signed up: {email}")
            return {"success": True, "user": response.user}
        else:
            return {"success": False, "error": "Signup failed"}
    
    except Exception as e:
        logger.error(f"❌ Signup error: {e}")
        return {"success": False, "error": str(e)}


def sign_in(email: str, password: str):
    """
    Sign in existing user
    
    Args:
        email: User email
        password: User password
    
    Returns:
        dict: User data or error
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            logger.info(f"✅ User signed in: {email}")
            # Store in session state
            st.session_state.user = response.user
            st.session_state.session = response.session
            return {"success": True, "user": response.user}
        else:
            return {"success": False, "error": "Invalid credentials"}
    
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        return {"success": False, "error": str(e)}


def sign_out():
    """
    Sign out current user
    """
    try:
        supabase.auth.sign_out()
        
        # Clear session state
        if 'user' in st.session_state:
            del st.session_state.user
        if 'session' in st.session_state:
            del st.session_state.session
        
        logger.info("✅ User signed out")
        return {"success": True}
    
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        return {"success": False, "error": str(e)}


def get_current_user():
    """
    Get currently logged in user from session state
    
    Returns:
        User object or None
    """
    return st.session_state.get('user', None)


def is_authenticated():
    """
    Check if user is authenticated
    
    Returns:
        bool: True if user is logged in
    """
    return 'user' in st.session_state and st.session_state.user is not None


def reset_password(email: str):
    """
    Send password reset email
    
    Args:
        email: User email
    
    Returns:
        dict: Success or error
    """
    try:
        response = supabase.auth.reset_password_for_email(email)
        logger.info(f"✅ Password reset email sent to: {email}")
        return {"success": True}
    
    except Exception as e:
        logger.error(f"❌ Password reset error: {e}")
        return {"success": False, "error": str(e)}