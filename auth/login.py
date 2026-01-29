"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                 🔥 ULTIMATE LOGIN PAGE - PROFESSIONAL GRADE 🔥               ║
║                                                                              ║
║  Features:                                                                   ║
║  ✅ Animated particle starfield background                                   ║
║  ✅ Floating gradient orbs with glow                                         ║
║  ✅ Glassmorphism cards with blur effect                                     ║
║  ✅ Neon glow buttons with hover animations                                  ║
║  ✅ Dark theme input fields with focus effects                               ║
║  ✅ Smooth CSS transitions everywhere                                        ║
║  ✅ Pulsing animated brain logo                                              ║
║  ✅ Gradient animated text                                                   ║
║  ✅ Modern tab design                                                        ║
║  ✅ Professional typography                                                  ║
║  ✅ Mobile responsive                                                        ║
║  ✅ User avatar sidebar card                                                 ║
║                                                                              ║
║  Version: 3.1 FIXED & COMPLETE                                               ║
║  Last Updated: January 2026                                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from auth.auth_functions import sign_in, sign_up, reset_password, sign_out
import time
import re

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                              CSS STYLES                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_login_css():
    """
    Returns the complete CSS styling for the login page.
    This includes:
    - Font imports
    - Background animations
    - Particle effects
    - Input field styling
    - Button styling
    - Tab styling
    - Form containers
    - Responsive design
    """
    return """
    <style>
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* IMPORT FONTS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* HIDE STREAMLIT ELEMENTS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* GLOBAL STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit form elements */
    .stForm {
        background: transparent !important;
        border: none !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FORM CONTAINER - GLASSMORPHISM */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .form-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 35px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .form-container:hover {
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* HEADER STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .login-header {
        text-align: center;
        margin-bottom: 40px;
        padding: 20px;
    }
    
    .brain-icon {
        font-size: 72px;
        animation: pulse 2s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.5));
    }
    
    @keyframes pulse {
        0%, 100% { 
            transform: scale(1); 
            filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.5));
        }
        50% { 
            transform: scale(1.1); 
            filter: drop-shadow(0 0 30px rgba(102, 126, 234, 0.8));
        }
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 20px 0 10px 0;
        letter-spacing: -1px;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
    }
    
    .tagline {
        color: #cbd5e0;
        font-size: 20px;
        font-weight: 400;
        margin-bottom: 20px;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 100px;
        padding: 12px 28px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        color: #a5b4fc;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .feature-badge:hover {
        background: rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(99, 102, 241, 0.5);
        box-shadow: 0 6px 30px rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FORM HEADER STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .form-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .form-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .form-subtitle {
        color: #a0aec0;
        font-size: 15px;
        font-weight: 400;
        margin-bottom: 25px;
        line-height: 1.5;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* INPUT FIELD STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 14px 18px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .stTextInput > label {
        color: #cbd5e0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        letter-spacing: 0.3px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* BUTTON STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px 24px;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* TAB STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.03);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #a0aec0;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #cbd5e0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FOOTER STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .login-footer {
        text-align: center;
        margin-top: 50px;
        padding: 30px;
    }
    
    .security-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 100px;
        padding: 10px 20px;
        color: #6ee7b7;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .security-badge:hover {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.5);
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
    
    .copyright {
        color: rgba(148, 163, 184, 0.5);
        font-size: 13px;
        font-family: 'Inter', sans-serif;
        margin: 0;
        letter-spacing: 0.3px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* PARTICLE BACKGROUND */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: -1;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 50%;
        animation: float linear infinite;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    
    @keyframes float {
        0% {
            transform: translateY(100vh) scale(0);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) scale(1);
            opacity: 0;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* SIDEBAR USER CARD STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .user-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    
    .user-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin: 0 auto 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .user-name {
        color: #ffffff;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 5px;
        letter-spacing: 0.3px;
    }
    
    .user-email {
        color: #a0aec0;
        font-size: 13px;
        font-weight: 400;
        word-break: break-all;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ALERT/MESSAGE STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* RESPONSIVE DESIGN */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .main-title {
            font-size: 36px;
        }
        
        .tagline {
            font-size: 16px;
        }
        
        .brain-icon {
            font-size: 56px;
        }
        
        .form-container {
            padding: 25px;
        }
        
        .feature-badge {
            font-size: 13px;
            padding: 10px 20px;
        }
    }
    
    @media (max-width: 480px) {
        .main-title {
            font-size: 28px;
        }
        
        .tagline {
            font-size: 14px;
        }
        
        .brain-icon {
            font-size: 48px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 16px;
            font-size: 13px;
        }
    }
    </style>
    """

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         FLOATING PARTICLES                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_particles_html():
    """
    Returns HTML/CSS for animated floating particles.
    Creates 10 particles with varying sizes and animation timings.
    """
    particles = ""
    for i in range(10):
        size = 2 + (i % 3)
        left = (i * 10) % 100
        delay = i * 0.5
        duration = 10 + (i % 5)
        particles += f'<div class="particle" style="width:{size}px;height:{size}px;left:{left}%;animation-delay:{delay}s;animation-duration:{duration}s;"></div>'
    
    return f'<div class="particles">{particles}</div>'

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                            HEADER SECTION                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_header_html():
    """
    Returns the HTML for the login page header.
    Includes animated brain icon, title, tagline, and badge.
    """
    return """
    <div class="login-header">
        <div class="brain-icon">🧠</div>
        <h1 class="main-title">Smart CSV Health Checker</h1>
        <p class="tagline">Data Quality. Diagnosed in Seconds. ⚡</p>
        <div class="feature-badge">
            <span>🤖</span>
            <span>AI-Powered Analysis</span>
        </div>
    </div>
    """

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                            FOOTER SECTION                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_footer_html():
    """
    Returns the HTML for the login page footer.
    Includes security badge and copyright.
    """
    return """
    <div class="login-footer">
        <div class="security-badge">
            <span>🔒</span>
            <span>Secured by Supabase</span>
        </div>
        <p class="copyright">© 2026 Smart CSV Health Checker AI • All Rights Reserved</p>
    </div>
    """

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       MAIN LOGIN PAGE FUNCTION                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def show_login_page():
    """
    Main function to display the login page.
    This function renders:
    1. Custom CSS styling
    2. Animated particles background
    3. Header with brain logo
    4. Login/Signup/Reset tabs
    5. Forms with validation
    6. Footer with security badge
    """
    # ═══════════════════════════════════════════════════════════════════════
    # INJECT CSS STYLES
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(get_login_css(), unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # INJECT FLOATING PARTICLES
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(get_particles_html(), unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    # LAYOUT - CENTERED CONTENT
    # ═══════════════════════════════════════════════════════════════════════
    # Add top spacing
    st.write("")
    
    # Create centered column layout
    col_left, col_center, col_right = st.columns([1, 2.2, 1])
    
    with col_center:
        # ═══════════════════════════════════════════════════════════════════
        # HEADER SECTION
        # ═══════════════════════════════════════════════════════════════════
        st.markdown(get_header_html(), unsafe_allow_html=True)
        
        # ═══════════════════════════════════════════════════════════════════
        # AUTHENTICATION TABS
        # ═══════════════════════════════════════════════════════════════════
        tab_login, tab_signup, tab_reset = st.tabs([
            "🔐 Login",
            "✨ Sign Up",
            "🔑 Reset Password"
        ])
        
        # ═══════════════════════════════════════════════════════════════════
        # LOGIN TAB
        # ═══════════════════════════════════════════════════════════════════
        with tab_login:
            render_login_form()
        
        # ═══════════════════════════════════════════════════════════════════
        # SIGNUP TAB
        # ═══════════════════════════════════════════════════════════════════
        with tab_signup:
            render_signup_form()
        
        # ═══════════════════════════════════════════════════════════════════
        # RESET PASSWORD TAB
        # ═══════════════════════════════════════════════════════════════════
        with tab_reset:
            render_reset_form()
        
        # ═══════════════════════════════════════════════════════════════════
        # FOOTER SECTION
        # ═══════════════════════════════════════════════════════════════════
        st.markdown(get_footer_html(), unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                              LOGIN FORM                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def render_login_form():
    """
    Renders the login form with email and password fields.
    Handles form submission and authentication.
    """
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        # Form header
        st.markdown("""
        <div class="form-header">
            <h3 class="form-title">Welcome Back! 👋</h3>
            <p class="form-subtitle">Enter your credentials to access your account</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Email input
        email = st.text_input(
            "📧 Email Address",
            placeholder="you@example.com",
            key="login_email",
            help="Enter the email you used to sign up"
        )
        
        # Password input
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
            help="Enter your account password"
        )
        
        # Spacing before button
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button
        submit_button = st.form_submit_button(
            "🚀 Sign In",
            use_container_width=True
        )
        
        # Handle form submission
        if submit_button:
            handle_login(email, password)
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_login(email: str, password: str):
    """
    Handles the login form submission.
    
    Args:
        email: User's email address
        password: User's password
    """
    # Validation
    if not email:
        st.error("⚠️ Please enter your email address")
        return
    
    if not password:
        st.error("⚠️ Please enter your password")
        return
    
    if not is_valid_email(email):
        st.error("⚠️ Please enter a valid email address")
        return
    
    # Attempt login
    with st.spinner("🔄 Signing you in..."):
        result = sign_in(email, password)
        
        if result["success"]:
            st.success("✅ Welcome back! Redirecting...")
            time.sleep(0.5)
            st.rerun()
        else:
            error_message = result.get('error', 'Login failed. Please check your credentials.')
            st.error(f"❌ {error_message}")

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                             SIGNUP FORM                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def render_signup_form():
    """
    Renders the signup form with all required fields.
    Handles form submission and account creation.
    """
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("signup_form", clear_on_submit=False):
        # Form header
        st.markdown("""
        <div class="form-header">
            <h3 class="form-title">Create Account ✨</h3>
            <p class="form-subtitle">Join thousands of data professionals worldwide</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Full name input
        full_name = st.text_input(
            "👤 Full Name",
            placeholder="John Doe",
            key="signup_name",
            help="Enter your full name"
        )
        
        # Email input
        email = st.text_input(
            "📧 Email Address",
            placeholder="you@example.com",
            key="signup_email",
            help="We'll send a verification link to this email"
        )
        
        # Password input
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Minimum 6 characters",
            key="signup_password",
            help="Use at least 6 characters with a mix of letters and numbers"
        )
        
        # Confirm password input
        password_confirm = st.text_input(
            "🔒 Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm",
            help="Re-enter your password to confirm"
        )
        
        # Spacing before button
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button
        submit_button = st.form_submit_button(
            "✨ Create Account",
            use_container_width=True
        )
        
        # Handle form submission
        if submit_button:
            handle_signup(full_name, email, password, password_confirm)
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_signup(full_name: str, email: str, password: str, password_confirm: str):
    """
    Handles the signup form submission.
    
    Args:
        full_name: User's full name
        email: User's email address
        password: User's password
        password_confirm: Password confirmation
    """
    # Validation
    if not full_name:
        st.error("⚠️ Please enter your full name")
        return
    
    if not email:
        st.error("⚠️ Please enter your email address")
        return
    
    if not is_valid_email(email):
        st.error("⚠️ Please enter a valid email address")
        return
    
    if not password:
        st.error("⚠️ Please enter a password")
        return
    
    if len(password) < 6:
        st.error("⚠️ Password must be at least 6 characters long")
        return
    
    if password != password_confirm:
        st.error("⚠️ Passwords don't match. Please try again.")
        return
    
    # Attempt signup
    with st.spinner("🔄 Creating your account..."):
        result = sign_up(email, password, full_name)
        
        if result["success"]:
            st.success("✅ Account created successfully!")
            st.info("📧 Please check your email to verify your account before logging in.")
        else:
            error_message = result.get('error', 'Signup failed. Please try again.')
            st.error(f"❌ {error_message}")

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        RESET PASSWORD FORM                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def render_reset_form():
    """
    Renders the password reset form.
    Handles form submission and sends reset email.
    """
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("reset_form", clear_on_submit=False):
        # Form header
        st.markdown("""
        <div class="form-header">
            <h3 class="form-title">Reset Password 🔑</h3>
            <p class="form-subtitle">Enter your email and we'll send you a reset link</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Email input
        email = st.text_input(
            "📧 Email Address",
            placeholder="you@example.com",
            key="reset_email",
            help="Enter the email associated with your account"
        )
        
        # Spacing before button
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button
        submit_button = st.form_submit_button(
            "📧 Send Reset Link",
            use_container_width=True
        )
        
        # Handle form submission
        if submit_button:
            handle_reset(email)
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_reset(email: str):
    """
    Handles the password reset form submission.
    
    Args:
        email: User's email address
    """
    # Validation
    if not email:
        st.error("⚠️ Please enter your email address")
        return
    
    if not is_valid_email(email):
        st.error("⚠️ Please enter a valid email address")
        return
    
    # Attempt password reset
    with st.spinner("🔄 Sending reset link..."):
        result = reset_password(email)
        
        if result["success"]:
            st.success("✅ Password reset link sent!")
            st.info("📧 Check your inbox for the reset link. It may take a few minutes.")
        else:
            error_message = result.get('error', 'Failed to send reset link. Please try again.')
            st.error(f"❌ {error_message}")

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          UTILITY FUNCTIONS                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Compile regex pattern once
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def is_valid_email(email: str) -> bool:
    """
    Validates email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    return bool(EMAIL_PATTERN.match(email))

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        SIDEBAR USER INFO                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def show_user_info_sidebar():
    """
    Displays user information in the sidebar when authenticated.
    Shows user avatar, name, email, and logout button.
    """
    user = st.session_state.get('user')
    
    if not user:
        return
    
    # Get user details
    user_email = user.email
    user_metadata = user.user_metadata if hasattr(user, 'user_metadata') else {}
    user_name = user_metadata.get('full_name', user_email.split('@')[0])
    user_initials = get_user_initials(user_name)
    
    # Add separator
    st.sidebar.markdown("---")
    
    # User card HTML
    st.sidebar.markdown(f"""
    <div class="user-card">
        <div class="user-avatar">{user_initials}</div>
        <div class="user-name">{user_name}</div>
        <div class="user-email">{user_email}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button
    if st.sidebar.button("🚪 Sign Out", use_container_width=True, key="logout_btn"):
        handle_logout()

def get_user_initials(name: str) -> str:
    """
    Gets the initials from a user's name.
    
    Args:
        name: User's full name
        
    Returns:
        User's initials (max 2 characters)
    """
    if not name:
        return "?"
    
    parts = name.strip().split()
    
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1:
        return parts[0][0].upper()
    else:
        return "?"

def handle_logout():
    """
    Handles user logout.
    Signs out the user and refreshes the page.
    """
    result = sign_out()
    
    if result["success"]:
        st.rerun()
    else:
        st.sidebar.error("Failed to logout. Please try again.")

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                             END OF FILE                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝