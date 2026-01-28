"""
CSS Styling for the application
Enhanced with advanced animations, glassmorphism, and modern UI effects
"""
import streamlit as st

def load_custom_css():
    """Load all custom CSS styles with advanced effects"""
    st.markdown("""
<style>
    /* ============================================================ */
    /* FONTS & BASE STYLES */
    /* ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ============================================================ */
    /* BACKGROUND & APP CONTAINER */
    /* ============================================================ */
    .stApp { 
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 50%, #0f1729 100%);
        background-attachment: fixed;
    }
    
    /* Animated gradient orbs */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(16, 185, 129, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%);
        animation: rotate 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
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
    /* HERO SECTION */
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
        filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.6));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-10px) scale(1.05); }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(
            135deg,
            #6366f1 0%,
            #8b5cf6 25%,
            #10b981 50%,
            #06b6d4 75%,
            #6366f1 100%
        );
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 8s ease infinite;
        margin: 0;
        text-align: center;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid rgba(99, 102, 241, 0.5);
        border-radius: 20px;
        padding: 0.3rem 1rem;
        font-size: 0.85rem;
        color: #a5b4fc;
        margin-top: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 10px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.6); }
    }
    
    /* ============================================================ */
    /* ENHANCED GLASSMORPHISM METRIC CARDS */
    /* ============================================================ */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        box-shadow: 
            0 8px 32px 0 rgba(0, 0, 0, 0.37),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
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
        background: linear-gradient(90deg, transparent, var(--card-color, #6366f1), transparent);
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
        background: radial-gradient(circle, var(--card-color, #6366f1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02) perspective(1000px) rotateX(2deg);
        box-shadow: 
            0 20px 60px 0 rgba(0, 0, 0, 0.5),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.2);
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
        color: #94a3b8;
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
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.8); }
    }
    
    /* ============================================================ */
    /* HEADERS - EMOJI FRIENDLY */
    /* ============================================================ */
    .main h1, .main h2, .main h3 {
        color: #e2e8f0;
        font-weight: 700;
    }
    
    .main h2 {
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
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
        background: linear-gradient(90deg, #6366f1, #8b5cf6, transparent);
        animation: underlineGlow 3s ease infinite;
    }
    
    @keyframes underlineGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .main h3 {
        font-size: 1.3rem;
        color: #a5b4fc;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Keep gradient flow animation for other uses */
    @keyframes gradientFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    /* ============================================================ */
    /* TABS */
    /* ============================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.02);
        padding: 0.5rem;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #e2e8f0;
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2)) !important;
        color: #a5b4fc !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
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
    /* ENHANCED BUTTONS WITH RIPPLE EFFECT */
    /* ============================================================ */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        position: relative;
        overflow: hidden;
        cursor: pointer;
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
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0px) scale(0.98);
    }
    
    /* Primary button glow */
    .stButton > button[kind="primary"] {
        box-shadow: 
            0 4px 15px rgba(99, 102, 241, 0.4),
            0 0 20px rgba(99, 102, 241, 0.2);
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 
            0 8px 25px rgba(99, 102, 241, 0.6),
            0 0 40px rgba(99, 102, 241, 0.4);
    }
    
    /* ============================================================ */
    /* FILE UPLOADER */
    /* ============================================================ */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 2px dashed rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 2rem;
        transition: all 0.3s;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.6);
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
    }
    
    /* ============================================================ */
    /* ENHANCED DATA TABLES */
    /* ============================================================ */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Table header */
    [data-testid="stDataFrame"] thead {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stDataFrame"] th {
        color: #a5b4fc !important;
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
        background: rgba(99, 102, 241, 0.1);
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
        border-radius: 12px;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
        animation: slideInRight 0.3s ease-out;
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
        background: rgba(99, 102, 241, 0.1) !important;
        border-left-color: #6366f1 !important;
    }
    
    /* ============================================================ */
    /* ANIMATED PROGRESS BAR */
    /* ============================================================ */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #10b981, #06b6d4);
        background-size: 200% 200%;
        animation: gradientFlow 3s ease infinite;
    }
    
    /* ============================================================ */
    /* CUSTOM LOADING SPINNER */
    /* ============================================================ */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
        border-right-color: #8b5cf6 !important;
        border-bottom-color: #10b981 !important;
        border-left-color: #06b6d4 !important;
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
    /* ENHANCED SIDEBAR */
    /* ============================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] h2 {
        color: #a5b4fc;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Sidebar widgets */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 1rem;
    }
    
    /* Sidebar expander */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.3s;
    }
    
    [data-testid="stSidebar"] [data-testid="stExpander"]:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* ============================================================ */
    /* TOOLTIPS */
    /* ============================================================ */
    [data-testid="stTooltipIcon"] {
        color: #a5b4fc;
        transition: all 0.3s;
    }
    
    [data-testid="stTooltipIcon"]:hover {
        color: #6366f1;
        transform: scale(1.2);
    }
    
    /* ============================================================ */
    /* EXPANDER */
    /* ============================================================ */
    .explanation-box {
        background: rgba(99, 102, 241, 0.1);
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .explanation-box h4 {
        color: #a5b4fc;
        margin-top: 0;
        font-size: 1.1rem;
    }
    
    /* ============================================================ */
    /* SCROLLBAR */
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
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6, #6366f1);
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
    }
    
    /* ============================================================ */
    /* KEYBOARD SHORTCUTS HINT */
    /* ============================================================ */
    .keyboard-hint {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #94a3b8;
        font-size: 0.75rem;
        z-index: 1000;
        opacity: 0;
        animation: fadeInUp 0.5s ease-out 2s forwards;
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

<script>
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