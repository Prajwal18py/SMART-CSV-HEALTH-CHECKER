import streamlit as st
from auth.auth_functions import sign_in, sign_up, reset_password, sign_out
import time
import re

# Configure page to prevent caching issues
st.set_page_config(
    page_title="DataForge Studio - Login",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                              CSS STYLES - ENHANCED                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_login_css():
    """
    Returns the complete CSS styling for the login page with UI enhancements.
    
    NEW ENHANCEMENTS:
    - Input focus glow with scale effect
    - Button hover lift with enhanced shadow
    - Brain pulse animation
    - Enhanced glassmorphism
    - Error shake animation
    - Password strength indicator
    - Micro-interactions
    """
    return """
    <style>
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* IMPORT FONTS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
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
        background: #0a0118;
        font-family: 'Inter', sans-serif;
        overflow-x: hidden;
    }
    
    /* ✨ ENHANCED: Animated gradient mesh background with smooth movement */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.25) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(168, 85, 247, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 90% 10%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
            linear-gradient(135deg, #0a0118 0%, #1a0b2e 50%, #160b28 100%);
        z-index: -2;
        animation: meshMove 20s ease-in-out infinite;
        background-size: 400% 400%;
    }
    
    @keyframes meshMove {
        0%, 100% { 
            transform: scale(1) rotate(0deg); 
            background-position: 0% 50%;
        }
        50% { 
            transform: scale(1.1) rotate(2deg); 
            background-position: 100% 50%;
        }
    }
    
    /* Hide default Streamlit form elements */
    .stForm {
        background: transparent !important;
        border: none !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ ENHANCED: FORM CONTAINER - ADVANCED GLASSMORPHISM */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .form-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05),
            0 0 0 1px rgba(168, 85, 247, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Shimmer effect on hover */
    .form-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
        transition: left 0.5s;
    }
    
    .form-container:hover::before {
        left: 100%;
    }
    
    /* ✨ ENHANCED: Lift and glow on hover */
    .form-container:hover {
        box-shadow: 
            0 12px 48px rgba(99, 102, 241, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 80px rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* HEADER STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .login-header {
        text-align: center;
        margin-bottom: 50px;
        padding: 30px 20px;
        position: relative;
    }
    
    /* ✨ ENHANCED: Brain pulse animation */
    .brain-icon {
        font-size: 80px;
        animation: brainPulse 2s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 30px rgba(168, 85, 247, 0.6));
        position: relative;
    }
    
    @keyframes brainPulse {
        0%, 100% { 
            transform: translateY(0px) scale(1); 
            filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.5));
        }
        50% { 
            transform: translateY(-10px) scale(1.05); 
            filter: drop-shadow(0 0 40px rgba(168, 85, 247, 0.8)) drop-shadow(0 0 80px rgba(236, 72, 153, 0.4));
        }
    }
    
    .main-title {
        font-size: 56px;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 25px 0 15px 0;
        letter-spacing: -2px;
        animation: gradientShift 8s ease infinite;
        position: relative;
        text-shadow: 0 0 80px rgba(168, 85, 247, 0.5);
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .tagline {
        color: rgba(203, 213, 224, 0.7);
        font-size: 20px;
        font-weight: 400;
        margin-bottom: 25px;
        letter-spacing: 1px;
        text-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
        font-family: 'Inter', sans-serif;
        opacity: 0.9;
    }
    
    /* ✨ ENHANCED: Feature badge with ripple effect */
    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 100px;
        padding: 14px 32px;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 4px 24px rgba(168, 85, 247, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: #c4b5fd;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    
    /* Ripple effect */
    .feature-badge::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .feature-badge:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .feature-badge:hover {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 1px solid rgba(168, 85, 247, 0.5);
        box-shadow: 
            0 8px 32px rgba(168, 85, 247, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: translateY(-3px);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FORM HEADER STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .form-header {
        text-align: center;
        margin-bottom: 35px;
    }
    
    .form-title {
        color: #ffffff;
        font-size: 30px;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .form-subtitle {
        color: rgba(160, 174, 192, 0.9);
        font-size: 15px;
        font-weight: 400;
        margin-bottom: 25px;
        line-height: 1.6;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ ENHANCED: INPUT FIELD STYLES WITH GLOW EFFECT */
    /* ═══════════════════════════════════════════════════════════════════════ */

    /* Target ALL Streamlit input containers */
    .stTextInput > div > div,
    .stTextInput > div > div > input,
    [data-testid="stTextInput"] > div > div,
    [data-testid="stTextInput"] input,
    [data-baseweb="input"] > div,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] {
        background: #1a1a2e !important;
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }

    /* ✨ ENHANCED: Main input styling with smooth transitions */
    .stTextInput > div > div > input,
    [data-testid="stTextInput"] input,
    [data-baseweb="input"] input {
        background: #1a1a2e !important;
        background-color: #1a1a2e !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        padding: 16px 20px !important;
        font-size: 15px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
    }

    /* Input container background */
    [data-baseweb="input"] {
        background-color: #1a1a2e !important;
        border-radius: 14px !important;
    }

    [data-baseweb="base-input"] {
        background-color: #1a1a2e !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* ✨ ENHANCED: Focus state with glow and scale */
    .stTextInput > div > div > input:focus,
    [data-testid="stTextInput"] input:focus,
    [data-baseweb="input"]:focus-within {
        background: #1f1f3a !important;
        background-color: #1f1f3a !important;
        border: 1.5px solid rgba(168, 85, 247, 0.6) !important;
        box-shadow: 
            0 0 0 4px rgba(168, 85, 247, 0.15),
            inset 0 2px 4px rgba(0, 0, 0, 0.2),
            0 0 30px rgba(168, 85, 247, 0.3) !important;
        outline: none !important;
        transform: scale(1.01);
    }

    /* Placeholder text */
    .stTextInput > div > div > input::placeholder,
    [data-testid="stTextInput"] input::placeholder,
    [data-baseweb="input"] input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.4) !important;
        opacity: 1 !important;
    }

    /* ✨ ENHANCED: Labels with icon support */
    .stTextInput > label,
    [data-testid="stTextInput"] label {
        color: rgba(203, 213, 224, 0.95) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 10px !important;
        letter-spacing: 0.3px !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        transition: color 0.2s ease;
    }

    /* Password field eye icon container */
    [data-testid="stTextInput"] > div > div,
    .stTextInput > div > div {
        background: #1a1a2e !important;
        background-color: #1a1a2e !important;
        border-radius: 14px !important;
    }

    /* ✨ ENHANCED: Password toggle button (eye icon) with hover */
    button[kind="icon"],
    [data-testid="stTextInput"] button,
    .stTextInput button {
        background: transparent !important;
        color: rgba(255, 255, 255, 0.6) !important;
        transition: all 0.2s ease !important;
    }

    button[kind="icon"]:hover,
    [data-testid="stTextInput"] button:hover,
    .stTextInput button:hover {
        color: #a78bfa !important;
        transform: scale(1.1);
    }

    /* Force ALL input elements */
    input, textarea {
        background: #1a1a2e !important;
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Chrome/Safari autofill fix */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 50px #1a1a2e inset !important;
        -webkit-text-fill-color: #ffffff !important;
        background-color: #1a1a2e !important;
        color: #ffffff !important;
        transition: background-color 5000s ease-in-out 0s !important;
        caret-color: #ffffff !important;
    }

    /* Firefox autofill */
    input:autofill {
        background: #1a1a2e !important;
        color: #ffffff !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ ENHANCED: BUTTON STYLES WITH LIFT EFFECT */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    button[kind="primary"],
    button[kind="secondary"] {
        width: 100%;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #8b5cf6 100%) !important;
        background-size: 200% 200%;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 18px 28px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 20px rgba(168, 85, 247, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        text-transform: uppercase;
        font-family: 'Space Grotesk', sans-serif;
        position: relative;
        overflow: hidden;
        animation: buttonGradient 3s ease infinite;
    }

    @keyframes buttonGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* Ripple effect on click */
    .stButton > button::before,
    [data-testid="stFormSubmitButton"] > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    /* ✨ ENHANCED: Hover state with lift */
    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 8px 30px rgba(168, 85, 247, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    }

    .stButton > button:hover::before,
    [data-testid="stFormSubmitButton"] > button:hover::before {
        width: 400px;
        height: 400px;
    }

    /* Active/pressed state */
    .stButton > button:active,
    [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(0px);
        box-shadow: 
            0 4px 15px rgba(168, 85, 247, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    /* Form submit button specific */
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #8b5cf6 100%) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Help text / hint text */
    .stTextInput small,
    [data-testid="stTextInput"] small,
    div[data-testid="InputInstructions"] {
        color: rgba(160, 174, 192, 0.7) !important;
        background: transparent !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ ENHANCED: TAB STYLES WITH SMOOTH TRANSITIONS */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.02);
        padding: 10px;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: rgba(160, 174, 192, 0.8);
        padding: 16px 32px;
        border-radius: 14px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.3px;
        font-family: 'Inter', sans-serif;
        position: relative;
    }
    
    /* Tab hover preview */
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(203, 213, 224, 0.95);
    }
    
    /* ✨ ENHANCED: Active tab with glow */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(99, 102, 241, 0.3) 100%);
        color: white !important;
        box-shadow: 
            0 4px 20px rgba(168, 85, 247, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FOOTER STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .login-footer {
        text-align: center;
        margin-top: 60px;
        padding: 30px;
    }
    
    .security-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 100px;
        padding: 12px 24px;
        color: #6ee7b7;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    .security-badge:hover {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.5);
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.3);
        transform: translateY(-2px);
    }
    
    .copyright {
        color: rgba(148, 163, 184, 0.4);
        font-size: 13px;
        font-family: 'Inter', sans-serif;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* FLOATING ORBS BACKGROUND */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .orbs {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: -1;
        pointer-events: none;
    }
    
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(60px);
        opacity: 0.4;
        animation: orbFloat 20s infinite ease-in-out;
    }
    
    .orb-1 {
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.3) 0%, transparent 70%);
        top: -200px;
        left: -200px;
        animation-duration: 25s;
    }
    
    .orb-2 {
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, transparent 70%);
        bottom: -150px;
        right: -150px;
        animation-duration: 30s;
        animation-delay: -5s;
    }
    
    .orb-3 {
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(236, 72, 153, 0.2) 0%, transparent 70%);
        top: 50%;
        left: 50%;
        animation-duration: 35s;
        animation-delay: -10s;
    }
    
    @keyframes orbFloat {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(100px, -100px) scale(1.1); }
        50% { transform: translate(-50px, 100px) scale(0.9); }
        75% { transform: translate(150px, 50px) scale(1.05); }
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
        background: rgba(255, 255, 255, 1);
        border-radius: 50%;
        animation: particleFloat linear infinite;
        box-shadow: 
            0 0 15px rgba(255, 255, 255, 1),
            0 0 30px rgba(168, 85, 247, 0.8),
            0 0 45px rgba(168, 85, 247, 0.6),
            0 0 60px rgba(99, 102, 241, 0.4);
    }
    
    @keyframes particleFloat {
        0% {
            transform: translateY(100vh) scale(0) rotate(0deg);
            opacity: 0;
        }
        5% {
            opacity: 1;
        }
        95% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) scale(1.5) rotate(360deg);
            opacity: 0;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* SIDEBAR USER CARD STYLES */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .user-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .user-card:hover {
        border: 1px solid rgba(168, 85, 247, 0.3);
        box-shadow: 
            0 12px 40px rgba(168, 85, 247, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .user-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin: 0 auto 18px;
        box-shadow: 
            0 8px 24px rgba(168, 85, 247, 0.4),
            inset 0 2px 0 rgba(255, 255, 255, 0.2);
        font-family: 'Space Grotesk', sans-serif;
        border: 3px solid rgba(255, 255, 255, 0.1);
    }
    
    .user-name {
        color: #ffffff;
        font-size: 19px;
        font-weight: 600;
        margin-bottom: 6px;
        letter-spacing: 0.3px;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .user-email {
        color: rgba(160, 174, 192, 0.8);
        font-size: 13px;
        font-weight: 400;
        word-break: break-all;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ ENHANCED: ALERT/MESSAGE STYLES WITH SHAKE ANIMATION */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .stAlert {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    /* Error alert shake animation */
    [data-testid="stAlert"][data-kind="error"] {
        animation: shake 0.5s;
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 3px solid #ef4444 !important;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }

    /* Success alert */
    [data-testid="stAlert"][data-kind="success"] {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 3px solid #10b981 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ NEW: PASSWORD STRENGTH INDICATOR */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .password-strength {
        margin-top: 8px;
        padding: 12px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }

    .strength-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 8px;
    }

    .strength-fill {
        height: 100%;
        transition: width 0.3s ease, background-color 0.3s ease;
        border-radius: 3px;
    }

    .strength-text {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .strength-weak { color: #ef4444; }
    .strength-fair { color: #f59e0b; }
    .strength-good { color: #10b981; }
    .strength-strong { color: #06b6d4; }

    .strength-fill-weak { background: linear-gradient(90deg, #ef4444, #dc2626); width: 25%; }
    .strength-fill-fair { background: linear-gradient(90deg, #f59e0b, #d97706); width: 50%; }
    .strength-fill-good { background: linear-gradient(90deg, #10b981, #059669); width: 75%; }
    .strength-fill-strong { background: linear-gradient(90deg, #06b6d4, #0891b2); width: 100%; }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* ✨ NEW: LOADING SPINNER ANIMATION */
    /* ═══════════════════════════════════════════════════════════════════════ */
    
    /* Override default Streamlit spinner */
    .stSpinner > div {
        border: 4px solid rgba(168, 85, 247, 0.1) !important;
        border-top: 4px solid #a855f7 !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        animation: spin 1s linear infinite !important;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Custom loading container */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        background: rgba(168, 85, 247, 0.05);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        margin: 20px 0;
    }
    
    /* Animated spinner */
    .custom-spinner {
        width: 56px;
        height: 56px;
        border: 5px solid rgba(168, 85, 247, 0.1);
        border-top: 5px solid #a855f7;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.3);
    }
    
    /* Pulsing dots */
    .loading-dots {
        display: flex;
        gap: 8px;
        margin-top: 15px;
    }
    
    .loading-dot {
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #a855f7, #6366f1);
        border-radius: 50%;
        animation: dotPulse 1.4s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
    }
    
    .loading-dot:nth-child(1) { animation-delay: 0s; }
    .loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .loading-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes dotPulse {
        0%, 100% { 
            transform: scale(0.8);
            opacity: 0.5;
        }
        50% { 
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    /* Loading text */
    .loading-text {
        color: #a5b4fc;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
        font-family: 'Space Grotesk', sans-serif;
        animation: textPulse 2s ease-in-out infinite;
    }
    
    @keyframes textPulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* Shimmer effect for loading state */
    .loading-shimmer {
        position: relative;
        overflow: hidden;
    }
    
    .loading-shimmer::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent
        );
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        100% { left: 100%; }
    }
    
    /* ═══════════════════════════════════════════════════════════════════════ */
    /* RESPONSIVE DESIGN */
    /* ═══════════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .main-title {
            font-size: 40px;
        }
        
        .tagline {
            font-size: 17px;
        }
        
        .brain-icon {
            font-size: 64px;
        }
        
        .form-container {
            padding: 30px 25px;
        }
        
        .feature-badge {
            font-size: 14px;
            padding: 12px 24px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 14px 20px;
            font-size: 14px;
        }
    }
    
    @media (max-width: 480px) {
        .main-title {
            font-size: 32px;
            letter-spacing: -1px;
        }
        
        .tagline {
            font-size: 15px;
        }
        
        .brain-icon {
            font-size: 56px;
        }
        
        .form-container {
            padding: 25px 20px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 18px;
            font-size: 13px;
        }
        
        .feature-badge {
            font-size: 13px;
            padding: 10px 20px;
        }
    }
    </style>
    """

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         FLOATING ORBS & PARTICLES                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_orbs_html():
    """
    Returns HTML for animated floating orbs background.
    """
    return '''
    <div class="orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>
    '''

def get_particles_html():
    """
    Returns HTML/CSS for animated floating particles.
    Creates 40 particles with varying sizes (3-8px) for highly visible star-like effect.
    """
    particles = ""
    for i in range(40):
        size = 3 + (i % 6)  # Sizes from 3-8px
        left = (i * 2.5) % 100
        delay = i * 0.3
        duration = 8 + (i % 10)
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
        <h1 class="main-title">DataForge Studio</h1>
        <p class="tagline">End-to-End ML Data Preparation ⚡</p>
        <div style="text-align: center; width: 100%; margin-top: 15px;">
            <span class="feature-badge" style="display: inline-flex;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A2.5 2.5 0 0 0 5 15.5A2.5 2.5 0 0 0 7.5 18a2.5 2.5 0 0 0 2.5-2.5A2.5 2.5 0 0 0 7.5 13m9 0a2.5 2.5 0 0 0-2.5 2.5a2.5 2.5 0 0 0 2.5 2.5a2.5 2.5 0 0 0 2.5-2.5a2.5 2.5 0 0 0-2.5-2.5Z"/>
                </svg>
                <span>AI-Powered ML Pipeline</span>
            </span>
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
        <p class="copyright">© 2026 DataForge Studio • All Rights Reserved</p>
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
    # INJECT FLOATING ORBS
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(get_orbs_html(), unsafe_allow_html=True)
    
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
        # APP FEATURES - QUICK HIGHLIGHTS
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("""
        <div style="
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <div style="padding: 12px;">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">🤖</div>
                <p style="color: #a5b4fc; font-weight: 600; font-size: 0.95rem; margin: 0;">AI-Powered Analysis</p>
                <p style="color: rgba(203, 213, 224, 0.7); font-size: 0.8rem; margin-top: 4px;">Auto-fix errors • Detect anomalies • Smart cleaning</p>
            </div>
            <div style="padding: 12px;">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">🛡️</div>
                <p style="color: #6ee7b7; font-weight: 600; font-size: 0.95rem; margin: 0;">100% Private & Secure</p>
                <p style="color: rgba(203, 213, 224, 0.7); font-size: 0.8rem; margin-top: 4px;">No cloud • Data never leaves your browser</p>
            </div>
            <div style="padding: 12px;">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">⚡</div>
                <p style="color: #c4b5fd; font-weight: 600; font-size: 0.95rem; margin: 0;">Zero Code Required</p>
                <p style="color: rgba(203, 213, 224, 0.7); font-size: 0.8rem; margin-top: 4px;">Click-based ML • 12 algorithms • Export Python</p>
            </div>
        </div>
        <div style="text-align: center; margin-bottom: 30px;">
            <p style="
                color: #fbbf24;
                font-weight: 600;
                font-size: 0.9rem;
                margin: 0;
                letter-spacing: 0.5px;
            ">
                ⭐ 100% Free Forever • No Limits • No Setup Required
            </p>
        </div>
        """, unsafe_allow_html=True)
        
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
# ║                      ✨ CUSTOM LOADING COMPONENT                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def show_loading(message="Loading..."):
    """
    Display a beautiful custom loading animation.
    
    Args:
        message: Loading message to display
        
    Usage:
        container = show_loading("Signing you in...")
        # Do your processing
        container.empty()  # Remove loading
    """
    container = st.empty()
    
    container.markdown(f"""
    <div class="loading-container loading-shimmer">
        <div class="custom-spinner"></div>
        <div class="loading-text">{message}</div>
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return container

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
            <h3 class="form-title">Welcome Back! <span style="display: inline-block; -webkit-text-fill-color: initial; background: none;">👋</span></h3>
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
            "🚀 Sign In"
        )
        
        # Handle form submission
        if submit_button:
            handle_login(email, password)
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_login(email: str, password: str):
    """
    Handles the login form submission with beautiful loading animation.
    
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
    
    # ✨ ENHANCED: Custom loading with animated messages
    loading = show_loading("🔍 Verifying credentials...")
    time.sleep(0.5)
    
    loading.markdown("""
    <div class="loading-container loading-shimmer">
        <div class="custom-spinner"></div>
        <div class="loading-text">✨ Loading your workspace...</div>
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Attempt login
    result = sign_in(email, password)
    
    if result["success"]:
        loading.markdown("""
        <div class="loading-container loading-shimmer">
            <div class="custom-spinner"></div>
            <div class="loading-text">🚀 Almost there...</div>
            <div class="loading-dots">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.3)
        
        loading.empty()
        st.success("✅ Welcome back! Redirecting...")
        time.sleep(0.5)
        st.rerun()
    else:
        loading.empty()
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
            <h3 class="form-title">Create Account <span style="display: inline-block; -webkit-text-fill-color: initial; background: none;">✨</span></h3>
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
        
        # ✨ NEW: Password strength indicator
        if password:
            strength, strength_class, strength_fill_class = calculate_password_strength(password)
            st.markdown(f"""
            <div class="password-strength">
                <div class="strength-bar">
                    <div class="strength-fill {strength_fill_class}"></div>
                </div>
                <div class="strength-text {strength_class}">
                    {strength}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
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
            "✨ Create Account"
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
    
    # ✨ ENHANCED: Custom loading animation
    loading = show_loading("🔄 Creating your account...")
    time.sleep(0.5)
    
    result = sign_up(email, password, full_name)
    
    loading.empty()
    
    if result["success"]:
        st.success("✅ Account created successfully!")
        st.markdown("""
            <div style="
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 1rem;
                backdrop-filter: blur(10px);
            ">
                <h4 style="color: #a5b4fc; margin-top: 0; font-size: 1.1rem;">📧 Verification Email Sent!</h4>
                <p style="color: #e2e8f0; margin-bottom: 1rem;">Please check your inbox for the verification link.</p>
                <div style="
                    background: rgba(245, 158, 11, 0.1);
                    border-left: 3px solid #f59e0b;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-top: 1rem;
                ">
                    <p style="color: #fbbf24; font-weight: 600; margin: 0 0 0.5rem 0;">⚠️ Didn't receive the email?</p>
                    <ul style="color: #cbd5e0; margin: 0; padding-left: 1.2rem; font-size: 0.9rem;">
                        <li>Check your <strong>spam/junk folder</strong></li>
                        <li>Wait 2-3 minutes for delivery</li>
                        <li>Verify your email address is correct</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
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
            <h3 class="form-title">Reset Password <span style="display: inline-block; -webkit-text-fill-color: initial; background: none;">🔑</span></h3>
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
            "📧 Send Reset Link"
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
    
    # ✨ ENHANCED: Custom loading animation
    loading = show_loading("🔄 Sending reset link...")
    time.sleep(0.5)
    
    result = reset_password(email)
    
    loading.empty()
    
    if result["success"]:
        st.success("✅ Password reset link sent!")
        st.markdown("""
            <div style="
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 1rem;
                backdrop-filter: blur(10px);
            ">
                <h4 style="color: #a5b4fc; margin-top: 0; font-size: 1.1rem;">📧 Reset Link Sent!</h4>
                <p style="color: #e2e8f0; margin-bottom: 1rem;">Check your inbox for the password reset link.</p>
                <div style="
                    background: rgba(245, 158, 11, 0.1);
                    border-left: 3px solid #f59e0b;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-top: 1rem;
                ">
                    <p style="color: #fbbf24; font-weight: 600; margin: 0 0 0.5rem 0;">⚠️ Didn't receive the email?</p>
                    <ul style="color: #cbd5e0; margin: 0; padding-left: 1.2rem; font-size: 0.9rem;">
                        <li>Check your <strong>spam/junk folder</strong></li>
                        <li>Wait 2-3 minutes for delivery</li>
                        <li>Verify your email address is correct</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
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

def calculate_password_strength(password: str) -> tuple:
    """
    ✨ NEW: Calculate password strength and return appropriate classes.
    
    Args:
        password: Password to evaluate
        
    Returns:
        Tuple of (strength_text, strength_class, fill_class)
    """
    score = 0
    
    # Length check
    if len(password) >= 6:
        score += 1
    if len(password) >= 10:
        score += 1
    
    # Character variety
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[0-9]', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # Determine strength
    if score <= 2:
        return ("🔴 Weak", "strength-weak", "strength-fill-weak")
    elif score <= 3:
        return ("🟡 Fair", "strength-fair", "strength-fill-fair")
    elif score <= 4:
        return ("🟢 Good", "strength-good", "strength-fill-good")
    else:
        return ("🟢 Strong", "strength-strong", "strength-fill-strong")

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
    if st.sidebar.button("🚪 Sign Out", key="logout_btn"):
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