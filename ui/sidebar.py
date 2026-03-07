"""
Sidebar Component - FIXED VERSION
Settings and configuration options with enhanced UI and CENTERED Sign Out button
"""
import streamlit as st

# ══════════════════════════════════════════════════════════════════════
# ENHANCED SIDEBAR CSS
# ══════════════════════════════════════════════════════════════════════
SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* Sidebar section headers */
[data-testid="stSidebar"] h3 {
    font-family: 'Syne', sans-serif !important;
    color: #c7d2fe !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding-top: 1rem !important;
}

/* Sidebar labels */
[data-testid="stSidebar"] label {
    font-size: 0.85rem !important;
    color: rgba(203,213,224,0.9) !important;
}

/* Sidebar dividers */
[data-testid="stSidebar"] hr {
    border-color: rgba(99,102,241,0.2) !important;
    margin: 1.2rem 0 !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] .stSelectbox {
    transition: all 0.3s ease;
}

/* Sidebar checkbox */
[data-testid="stSidebar"] .stCheckbox {
    padding: 0.3rem 0;
}

/* Sidebar expanders */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: rgba(99,102,241,0.08) !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
    background: rgba(99,102,241,0.15) !important;
}

/* Sidebar info boxes */
[data-testid="stSidebar"] .stAlert {
    font-size: 0.78rem !important;
    padding: 0.6rem !important;
    border-radius: 8px !important;
}
</style>
"""


def render_sidebar():
    """
    Render sidebar with app settings and enhanced UI
    
    Returns:
        Dictionary with user settings
    """
    # Apply sidebar CSS
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown("---")
        
        # ========================================================
        # AI DETECTION SETTINGS
        # ========================================================
        st.markdown("### 🎯 AI Detection")
        sensitivity = st.select_slider(
            "Anomaly Sensitivity",
            options=['low', 'medium', 'high'],
            value='medium',
            help="Higher sensitivity detects more anomalies but may have false positives"
        )
        
        # Map sensitivity to contamination rate
        sensitivity_map = {
            'low': 0.02,
            'medium': 0.05,
            'high': 0.10
        }
        ai_sensitivity = sensitivity_map[sensitivity]
        
        # Show info about current setting
        if sensitivity == 'high':
            st.caption("🔍 High: Detects ~10% of data as anomalies")
        elif sensitivity == 'medium':
            st.caption("⚖️ Medium: Detects ~5% of data as anomalies")
        else:
            st.caption("🎯 Low: Detects ~2% of data as anomalies")
        
        st.markdown("---")
        
        # ========================================================
        # IMPUTATION SETTINGS
        # ========================================================
        st.markdown("### 🔧 Data Cleaning")
        imputation_display = st.selectbox(
            "Missing Value Strategy",
            options=['MICE (Recommended)', 'Mean/Mode', 'Drop Rows'],
            index=0,
            help="MICE (Multivariate Imputation by Chained Equations) is recommended for best results"
        )
        
        # Map display name to internal name
        imputation_map = {
            'MICE (Recommended)': 'mice',
            'Mean/Mode': 'mean',
            'Drop Rows': 'drop'
        }
        imputation_method = imputation_map[imputation_display]
        
        # Show info about MICE
        if 'MICE' in imputation_display:
            st.info("""
            **MICE** uses multiple iterations to model each feature with missing values as a function of other features. 
            More sophisticated than simple mean/median imputation.
            """, icon="💡")
        
        # Outlier sensitivity
        outlier_sensitivity = st.slider(
            "Outlier Detection (IQR)",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.5,
            help="IQR multiplier: 1.5 = standard, 3.0 = lenient"
        )
        
        st.markdown("---")
        
        # ========================================================
        # VISUALIZATION SETTINGS
        # ========================================================
        st.markdown("### 📊 Visualization")
        show_3d_pca = st.checkbox(
            "Enable 3D PCA",
            value=False,
            help="Show PCA results in 3D (requires 3+ numeric columns)"
        )
        
        chart_theme = st.selectbox(
            "Chart Theme",
            ["Dark (Default)", "Light", "Colorblind-Safe"],
            help="Color scheme for visualizations"
        )
        
        st.markdown("---")
        
        # ========================================================
        # EXPORT SETTINGS
        # ========================================================
        st.markdown("### 📦 Export Options")
        include_code = st.checkbox(
            "Include Python Code",
            value=True,
            help="Include executable Python code in exports"
        )
        
        include_visualizations = st.checkbox(
            "Include Visualizations",
            value=True,
            help="Include charts in PDF exports"
        )
        
        export_format = st.selectbox(
            "Default Export Format",
            ["CSV", "Excel", "Parquet", "JSON"],
            help="Default format for data downloads"
        )
        
        st.markdown("---")
        
        # ========================================================
        # ADVANCED OPTIONS
        # ========================================================
        with st.expander("🔬 Advanced Options"):
            max_categories = st.number_input(
                "Max Categories to Display",
                min_value=5,
                max_value=50,
                value=20,
                help="Maximum unique values to show for categorical columns"
            )
            
            correlation_threshold = st.slider(
                "Correlation Threshold",
                min_value=0.5,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="Minimum correlation to highlight"
            )
            
            pca_components = st.number_input(
                "Default PCA Components",
                min_value=2,
                max_value=10,
                value=3,
                help="Number of principal components for PCA"
            )
            
            auto_save = st.checkbox(
                "Auto-save Session State",
                value=False,
                help="Automatically save your work between sessions"
            )
        
        st.markdown("---")
        
        # ========================================================
        # PERFORMANCE SETTINGS
        # ========================================================
        with st.expander("⚡ Performance"):
            cache_data = st.checkbox(
                "Enable Data Caching",
                value=True,
                help="Cache processed data for faster reloads"
            )
            
            sample_large_data = st.checkbox(
                "Sample Large Datasets",
                value=False,
                help="Automatically sample datasets > 50K rows for faster analysis"
            )
            
            if sample_large_data:
                sample_size = st.number_input(
                    "Sample Size",
                    min_value=1000,
                    max_value=50000,
                    value=10000,
                    step=1000
                )
            else:
                sample_size = None
        
        st.markdown("---")
        
        # ========================================================
        # ABOUT SECTION
        # ========================================================
        with st.expander("ℹ️ About DataForge Studio"):
            st.markdown("""
            **DataForge Studio v3.1**
            
            A fully local ML data preparation platform. No cloud, no API keys, no subscription.
            
            **🎉 What's New in v3.1:**
            - 🤖 Model Builder (12 algorithms, production exports)
            - 📑 Dark-themed PDF reports (EDA, Model, Overview)
            - ⚖️ Pure NumPy SMOTE/ADASYN (no imblearn dependency)
            - 🔄 Smart data pipeline (auto-picks best processed version)
            - 📊 Enhanced visualizations & stale results detection
            
            **💪 Core Features:**
            - 🧠 AI-powered anomaly detection (Isolation Forest)
            - 📊 Complete EDA with correlation heatmaps & Q-Q plots
            - 🛠️ 3-mode data cleaning (Wizard, Auto-Repair, Manual)
            - 📐 6 skewness transformations with before/after previews
            - 🔧 Feature engineering (scaling, encoding, polynomial)
            - ⚖️ Imbalanced data handler (SMOTE, ADASYN, undersampling)
            - 🤖 Model training & export (.pkl + prediction code)
            - 📉 PCA dimensionality reduction (2D/3D)
            - 🔒 PII detection & masking (8+ types)
            - 🎲 Synthetic data generation
            - 💻 Production code generator (full pipeline)
            - 📄 Professional PDF reports
            
            **🏗️ Built With:**
            Streamlit • scikit-learn • pandas • NumPy • Plotly • ReportLab
            
            **📖 License:** Open Source
            """)
            
            st.caption("Made with ❤️ for data scientists & ML engineers")
        
        # Return settings dictionary
        return {
            # Core settings (required by app.py and analysis.py)
            'ai_sensitivity': ai_sensitivity,
            'imputation_method': imputation_method,
            'outlier_sensitivity': outlier_sensitivity,
            'show_3d_pca': show_3d_pca,
            
            # Display settings
            'sensitivity_label': sensitivity,
            'chart_theme': chart_theme,
            
            # Export settings
            'include_code': include_code,
            'include_visualizations': include_visualizations,
            'export_format': export_format,
            
            # Advanced settings
            'max_categories': max_categories,
            'correlation_threshold': correlation_threshold,
            'pca_components': pca_components,
            'auto_save': auto_save,
            
            # Performance settings
            'cache_data': cache_data,
            'sample_large_data': sample_large_data,
            'sample_size': sample_size
        }


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                        ✅ FIXED: USER INFO SIDEBAR                           ║
# ║                    Properly centered Sign Out button                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def show_user_info_sidebar():
    """
    Displays user information in the sidebar when authenticated.
    Shows user avatar, name, email, and CENTERED logout button.
    """
    from auth.auth_functions import sign_out
    
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
    <div style="
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
    ">
        <div style="
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
        ">{user_initials}</div>
        <div style="
            color: #ffffff;
            font-size: 19px;
            font-weight: 600;
            margin-bottom: 6px;
            letter-spacing: 0.3px;
            font-family: 'Space Grotesk', sans-serif;
        ">{user_name}</div>
        <div style="
            color: rgba(160, 174, 192, 0.8);
            font-size: 13px;
            font-weight: 400;
            word-break: break-all;
        ">{user_email}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ✅ FIX: Centered logout button using columns
    col_left, col_center, col_right = st.sidebar.columns([0.5, 2, 0.5])
    
    with col_center:
        if st.button("🚪 Sign Out", key="logout_btn", width='stretch'):
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
    from auth.auth_functions import sign_out
    
    result = sign_out()
    
    if result["success"]:
        st.rerun()
    else:
        st.sidebar.error("Failed to logout. Please try again.")