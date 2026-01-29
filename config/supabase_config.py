"""
Supabase Configuration
Handles connection to Supabase backend
"""
import streamlit as st
from supabase import create_client, Client
from utils.logger import get_logger

logger = get_logger()

def get_supabase_client() -> Client:
    """
    Get Supabase client using credentials from secrets
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        
        supabase: Client = create_client(url, key)
        logger.info("✅ Supabase client initialized successfully")
        return supabase
    
    except KeyError as e:
        logger.error(f"❌ Missing Supabase credentials in secrets.toml: {e}")
        st.error("⚠️ Supabase configuration missing. Please check secrets.toml")
        st.stop()
    
    except Exception as e:
        logger.error(f"❌ Error initializing Supabase client: {e}")
        st.error("⚠️ Failed to connect to Supabase")
        st.stop()

# Initialize client
supabase = get_supabase_client()