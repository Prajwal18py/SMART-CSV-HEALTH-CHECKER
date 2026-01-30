"""
CSS Styling for the application
Enhanced with advanced animations, glassmorphism, and modern UI effects
NOW MATCHES THE STUNNING LOGIN PAGE AESTHETIC
"""
import streamlit as st

def load_custom_css():
    """Load all custom CSS styles with advanced effects"""
    st.markdown("""
<style>
    /* ============================================================ */
    /* FONTS & BASE STYLES */
    /* ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ============================================================ */
    /* BACKGROUND & APP CONTAINER - MATCHES LOGIN PAGE */
    /* ============================================================ */
    .stApp { 
        background: #0a0118;
        overflow-x: hidden;
    }
    
    /* Animated gradient mesh background - MATCHES LOGIN */
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
    }
    
    @keyframes meshMove {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.1) rotate(2deg); }
    }
    
    /* Page fade-in animation */
    .main > div {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ============================================================ */
    /* HERO SECTION - MATCHES LOGIN */
    /* ============================================================ */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem 0 1rem 0;
        position: relative;
        z-index: 1;
    }
    
    .hero-icon {
        font-size: 4.5rem;
        filter: drop-shadow(0 0 30px rgba(168, 85, 247, 0.6));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { 
            transform: translateY(0px) scale(1); 
            filter: drop-shadow(0 0 30px rgba(168, 85, 247, 0.6));
        }
        50% { 
            transform: translateY(-10px) scale(1.05); 
            filter: drop-shadow(0 0 40px rgba(168, 85, 247, 0.8));
        }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 8s ease infinite;
        margin: 0;
        text-align: center;
        text-shadow: 0 0 80px rgba(168, 85, 247, 0.5);
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(203, 213, 224, 0.9);
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        text-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
    }
    
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 100px;
        padding: 0.5rem 1.5rem;
        font-size: 0.9rem;
        color: #c4b5fd;
        margin-top: 0.5rem;
        box-shadow: 
            0 4px 24px rgba(168, 85, 247, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: pulse 2s infinite;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .ai-badge:hover {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%);
        border: 1px solid rgba(168, 85, 247, 0.5);
        box-shadow: 
            0 8px 32px rgba(168, 85, 247, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: translateY(-3px);
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 24px rgba(168, 85, 247, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1); }
        50% { box-shadow: 0 4px 32px rgba(168, 85, 247, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1); }
    }
    
    /* ============================================================ */
    /* ENHANCED GLASSMORPHISM METRIC CARDS - MATCHES LOGIN */
    /* ============================================================ */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        box-shadow: 
            0 8px 32px 0 rgba(0, 0, 0, 0.4),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    
    /* Top border accent */
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--card-color, #a855f7), transparent);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    /* Glow effect on hover */
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, var(--card-color, #a855f7) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 12px 48px rgba(168, 85, 247, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(168, 85, 247, 0.2);
    }
    
    .metric-card:hover::before { opacity: 1; }
    .metric-card:hover::after { opacity: 0.1; }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--card-color, #ffffff) 0%, var(--card-color-light, #ffffff) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: rgba(148, 163, 184, 0.9);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    .metric-icon {
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 1.5rem;
        opacity: 0.2;
    }
    
    .ai-glow {
        animation: aiGlow 3s infinite;
    }
    
    @keyframes aiGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.4); }
        50% { box-shadow: 0 0 40px rgba(168, 85, 247, 0.8); }
    }
    
    /* ============================================================ */
    /* HEADERS - MATCHES LOGIN STYLE */
    /* ============================================================ */
    .main h1, .main h2, .main h3 {
        color: #e2e8f0;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .main h2 {
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(168, 85, 247, 0.2);
        position: relative;
    }
    
    /* Animated underline */
    .main h2::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 120px;
        height: 2px;
        background: linear-gradient(90deg, #a855f7, #6366f1, transparent);
        animation: underlineGlow 3s ease infinite;
    }
    
    @keyframes underlineGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .main h3 {
        font-size: 1.3rem;
        color: #c4b5fd;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* ============================================================ */
    /* TABS - MATCHES LOGIN */
    /* ============================================================ */
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
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(203, 213, 224, 0.95);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.3) 0%, rgba(99, 102, 241, 0.3) 100%);
        color: white !important;
        box-shadow: 
            0 4px 20px rgba(168, 85, 247, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    
    /* Tab transition */
    .stTabs [data-baseweb="tab-panel"] {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* ============================================================ */
    /* ENHANCED BUTTONS - MATCHES LOGIN */
    /* ============================================================ */
    .stButton > button {
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 50%, #8b5cf6 100%);
        background-size: 200% 200%;
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 20px rgba(168, 85, 247, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        cursor: pointer;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-family: 'Space Grotesk', sans-serif;
        animation: buttonGradient 3s ease infinite;
    }
    
    @keyframes buttonGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Ripple effect */
    .stButton > button::before {
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
    
    .stButton > button:hover::before {
        width: 400px;
        height: 400px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 8px 30px rgba(168, 85, 247, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
        box-shadow: 
            0 4px 15px rgba(168, 85, 247, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }
    
    /* ============================================================ */
    /* FILE UPLOADER - MATCHES LOGIN GLASSMORPHISM */
    /* ============================================================ */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px) saturate(180%);
        border: 2px dashed rgba(168, 85, 247, 0.3);
        border-radius: 24px;
        padding: 2.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(168, 85, 247, 0.6);
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 
            0 12px 40px rgba(168, 85, 247, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* ============================================================ */
    /* ENHANCED DATA TABLES */
    /* ============================================================ */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    /* Table header */
    [data-testid="stDataFrame"] thead {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(99, 102, 241, 0.2));
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stDataFrame"] th {
        color: #c4b5fd !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.75rem !important;
        padding: 1rem !important;
    }
    
    /* Table rows */
    [data-testid="stDataFrame"] tbody tr {
        transition: all 0.2s;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(168, 85, 247, 0.1);
        transform: scale(1.005);
    }
    
    /* Alternating row colors */
    [data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background: rgba(255, 255, 255, 0.02);
    }
    
    /* ============================================================ */
    /* ENHANCED ALERT BOXES */
    /* ============================================================ */
    .stAlert {
        border-radius: 14px;
        border-left: 4px solid;
        backdrop-filter: blur(20px);
        animation: slideInRight 0.3s ease-out;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Success alert */
    [data-baseweb="notification"][kind="success"] {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left-color: #10b981 !important;
    }
    
    /* Error alert */
    [data-baseweb="notification"][kind="error"] {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left-color: #ef4444 !important;
    }
    
    /* Warning alert */
    [data-baseweb="notification"][kind="warning"] {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left-color: #f59e0b !important;
    }
    
    /* Info alert */
    [data-baseweb="notification"][kind="info"] {
        background: rgba(168, 85, 247, 0.1) !important;
        border-left-color: #a855f7 !important;
    }
    
    /* ============================================================ */
    /* ANIMATED PROGRESS BAR */
    /* ============================================================ */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #a855f7, #6366f1, #8b5cf6, #a855f7);
        background-size: 200% 200%;
        animation: gradientFlow 3s ease infinite;
    }
    
    @keyframes gradientFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* ============================================================ */
    /* CUSTOM LOADING SPINNER */
    /* ============================================================ */
    .stSpinner > div {
        border-top-color: #a855f7 !important;
        border-right-color: #6366f1 !important;
        border-bottom-color: #8b5cf6 !important;
        border-left-color: #ec4899 !important;
        animation: spinnerRotate 1s linear infinite;
    }
    
    @keyframes spinnerRotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Loading text pulse */
    .stSpinner + div {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* ============================================================ */
    /* ENHANCED SIDEBAR - MATCHES LOGIN */
    /* ============================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0118 0%, #1a0b2e 100%);
        border-right: 1px solid rgba(168, 85, 247, 0.2);
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] h2 {
        color: #c4b5fd;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
        background: rgba(168, 85, 247, 0.1);
        border-radius: 12px;
        margin-bottom: 1rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Sidebar widgets */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 1rem;
    }
    
    /* Sidebar expander */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        margin-bottom: 0.5rem;
        transition: all 0.3s;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] [data-testid="stExpander"]:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(168, 85, 247, 0.3);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
    }
    
    /* ============================================================ */
    /* SIDEBAR USER CARD - FROM LOGIN PAGE */
    /* ============================================================ */
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
    
    /* ============================================================ */
    /* TOOLTIPS */
    /* ============================================================ */
    [data-testid="stTooltipIcon"] {
        color: #c4b5fd;
        transition: all 0.3s;
    }
    
    [data-testid="stTooltipIcon"]:hover {
        color: #a855f7;
        transform: scale(1.2);
    }
    
    /* ============================================================ */
    /* EXPANDER */
    /* ============================================================ */
    .explanation-box {
        background: rgba(168, 85, 247, 0.1);
        border-left: 4px solid #a855f7;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
    }
    
    .explanation-box h4 {
        color: #c4b5fd;
        margin-top: 0;
        font-size: 1.1rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* ============================================================ */
    /* SCROLLBAR - MATCHES LOGIN */
    /* ============================================================ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #a855f7, #6366f1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #6366f1, #a855f7);
    }
    
    /* ============================================================ */
    /* SKELETON LOADING ANIMATION */
    /* ============================================================ */
    .skeleton-loading {
        background: linear-gradient(90deg, 
            rgba(255,255,255,0.05) 25%, 
            rgba(255,255,255,0.1) 50%, 
            rgba(255,255,255,0.05) 75%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* ============================================================ */
    /* RESPONSIVE DESIGN */
    /* ============================================================ */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-icon {
            font-size: 3rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
        
        .stButton > button {
            padding: 0.65rem 1.5rem;
            font-size: 0.9rem;
        }
    }
    
    /* ============================================================ */
    /* KEYBOARD SHORTCUTS HINT */
    /* ============================================================ */
    .keyboard-hint {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        background: rgba(10, 1, 24, 0.9);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 12px;
        padding: 0.5rem 1rem;
        color: rgba(148, 163, 184, 0.9);
        font-size: 0.75rem;
        z-index: 1000;
        opacity: 0;
        animation: fadeInUp 0.5s ease-out 2s forwards;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.3);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>

<!-- Floating Particles - Matches Login Page -->
<div class="particles" id="particles"></div>
<div class="orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>

<style>
/* ============================================================ */
/* FLOATING PARTICLES - MATCHES LOGIN */
/* ============================================================ */
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

/* ============================================================ */
/* FLOATING ORBS - MATCHES LOGIN */
/* ============================================================ */
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
</style>

<script>
    // Create floating particles dynamically
    (function() {
        const particlesContainer = document.getElementById('particles');
        if (particlesContainer) {
            for (let i = 0; i < 40; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                const size = 3 + (i % 6);  // 3-8px sizes
                const left = (i * 2.5) % 100;
                const delay = i * 0.3;
                const duration = 8 + (i % 10);
                
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                particle.style.left = left + '%';
                particle.style.animationDelay = delay + 's';
                particle.style.animationDuration = duration + 's';
                
                particlesContainer.appendChild(particle);
            }
        }
    })();

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to run analysis
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const buttons = document.querySelectorAll('button[kind="primary"]');
            if (buttons.length > 0) buttons[0].click();
        }
        
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInputs = document.querySelectorAll('input[type="text"]');
            if (searchInputs.length > 0) searchInputs[0].focus();
        }
    });
    
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
</script>
""", unsafe_allow_html=True)