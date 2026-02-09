"""
Smart CSV AI Studio - Main Application
Enterprise-Grade Data Quality & Privacy Platform
NOW WITH SUPABASE AUTHENTICATION & DATABASE
"""
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Smart CSV AI Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== IMPORT AUTH ====================
from auth.login import show_login_page, show_user_info_sidebar
from auth.auth_functions import is_authenticated

# ==================== AUTHENTICATION CHECK ====================
if not is_authenticated():
    # Hide sidebar on login page
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    show_login_page()
    st.stop()

# ==================== USER IS AUTHENTICATED - SHOW APP ====================

# Import UI components
from ui.layout import setup_page_config, render_hero_section
from ui.styles import load_custom_css
from ui.sidebar import render_sidebar

# Import core functionality
from core.data_loader import handle_file_upload, generate_test_dataset
from core.type_detection import detect_column_types
from core.analysis import analyze_csv_with_ai

# Import tab renderers
from tabs.tab_overview import render_overview_tab
from tabs.tab_ai_deep_dive import render_ai_deep_dive_tab
from tabs.tab_fix_data import render_fix_data_tab
from tabs.tab_skewness import render_skewness_tab
from tabs.tab_pipeline import render_pipeline_tab
from tabs.tab_visualizations import render_visualizations_tab
from tabs.tab_pca import render_pca_tab
from tabs.tab_code import render_code_tab
from tabs.tab_deep_profile import render_deep_profile_tab
from tabs.tab_compare import render_compare_tab
from tabs.tab_synthetic import render_synthetic_tab
from tabs.tab_dashboard import render_dashboard_tab

# Import export utilities
from export.pdf_generator import generate_pdf
from visualization.charts import render_overview_metrics, render_dataset_overview_cards

# Import database functions
from database.db_functions import save_analysis

import time


def main():
    """Main application flow"""
    # 1. Setup page configuration
    setup_page_config()
    
    # 2. Load custom CSS
    load_custom_css()
    
    # Add enhanced CSS for landing page
    st.markdown("""
    <style>
    /* Enhanced file uploader styling */
    [data-testid="stFileUploader"] {
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 2px dashed rgba(99, 102, 241, 0.5) !important;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.8) !important;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Smooth scroll behavior */
    html {
        scroll-behavior: smooth;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 3. Show user info in sidebar
    show_user_info_sidebar()
    
    # 4. Render sidebar and get settings
    settings = render_sidebar()
    
    # 5. Render hero section
    render_hero_section()
    
    # 6. File upload
    uploaded_file = st.file_uploader(
        "📂 Drop your CSV file here or click to browse",
        type=['csv']
    )
    
    # 7. Handle file upload or show landing page
    if uploaded_file:
        # Load and validate data
        df = handle_file_upload(uploaded_file)
        
        if df is None:
            st.stop()
        
        # Detect column types
        col_types, df = detect_column_types(df)
        
        # Show dataset overview cards
        render_dataset_overview_cards(df)
        
        # Run AI analysis with progress tracking
        progress_bar = st.progress(0, text="🚀 Starting analysis...")
        start_time = time.time()
        
        progress_bar.progress(0.3, text="🔍 Analyzing data quality...")
        results = analyze_csv_with_ai(
            df,
            col_types,
            settings['ai_sensitivity'],
            settings['imputation_method']
        )
        
        progress_bar.progress(1.0, text="✅ Complete!")
        elapsed = time.time() - start_time
        time.sleep(0.3)
        progress_bar.empty()
        
        # Success message
        from features.statistics import get_health_grade
        st.success(
            f"✅ Analysis complete in {elapsed:.2f}s • "
            f"Health Grade: **{get_health_grade(results['health_score'])}**"
        )
        
        # ==================== AUTO-SAVE TO DATABASE ====================
        # Save analysis to database automatically
        if 'last_saved_file' not in st.session_state or st.session_state.last_saved_file != uploaded_file.name:
            health_score = results.get('health_score', 0)
            issues_summary = results.get('issues_summary', {})
            
            save_result = save_analysis(
                filename=uploaded_file.name,
                health_score=health_score,
                total_rows=len(df),
                total_columns=len(df.columns),
                issues_high=issues_summary.get('High', 0),
                issues_medium=issues_summary.get('Medium', 0),
                issues_low=issues_summary.get('Low', 0),
                analysis_data={"column_types": col_types}
            )
            
            if save_result['success']:
                st.session_state.last_saved_file = uploaded_file.name
                st.toast("✅ Analysis saved to your history!", icon="💾")
        
        # Display metrics
        st.markdown("---")
        render_overview_metrics(df, results, col_types)
        st.write("##")
        
        # ==================== RENDER TABS ====================
        tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
            "📊 Dashboard",
            "📋 Overview",
            "🧠 AI Deep Dive",
            "🛠️ Fix Data",
            "📐 Skewness",
            "🔧 Pipeline",
            "📊 Visualizations",
            "📉 PCA",
            "💻 Code",
            "🔒 Deep Profile",
            "📈 Compare",
            "🎲 Synthetic Data"
        ])
        
        with tab0:
            render_dashboard_tab()
        
        with tab1:
            render_overview_tab(df, results, col_types)
        
        with tab2:
            render_ai_deep_dive_tab(df, results, col_types, settings)
        
        with tab3:
            render_fix_data_tab(df, results, col_types, settings)
        
        with tab4:
            # Smart data source selection for Skewness tab
            current_df = st.session_state.get('global_cleaned_df')
            if current_df is None:
                current_df = st.session_state.get('skew_fixed_df')
            if current_df is None:
                current_df = df
            render_skewness_tab(current_df, settings)
        
        with tab5:
            render_pipeline_tab(df)
        
        with tab6:
            # Smart data source selection for Visualizations tab
            viz_df = st.session_state.get('skew_fixed_df')
            if viz_df is None:
                viz_df = st.session_state.get('global_cleaned_df')
            if viz_df is None:
                viz_df = df
            render_visualizations_tab(viz_df, col_types, results)
        
        with tab7:
            # Smart data source selection for PCA tab
            pca_df = st.session_state.get('skew_fixed_df')
            if pca_df is None:
                pca_df = st.session_state.get('global_cleaned_df')
            if pca_df is None:
                pca_df = df
            render_pca_tab(pca_df, results, col_types)
        
        with tab8:
            render_code_tab(col_types, settings)
        
        with tab9:
            render_deep_profile_tab(df)
        
        with tab10:
            render_compare_tab(df)
        
        with tab11:
            render_synthetic_tab(df, col_types)
        
        # Export buttons
        st.markdown("---")
        col_pdf, col_csv = st.columns(2)
        
        with col_pdf:
            st.download_button(
                "📄 Download PDF Report",
                generate_pdf(df, results),
                "ai_health_report.pdf",
                "application/pdf",
                width="stretch"
            )
        
        with col_csv:
            summary_data = (
                results['stats']['missing_info'].to_csv(index=False)
                if not results['stats']['missing_info'].empty
                else "No issues found"
            )
            st.download_button(
                "📊 Download Analysis Summary",
                summary_data,
                "analysis_summary.csv",
                "text/csv",
                width="stretch"
            )
    
    else:
        # Landing page
        render_landing_page()


def render_landing_page():
    """Render enhanced professional landing page"""
    
    # CSV Upload prompt FIRST - get users to action faster
    st.info("👆 **Upload a CSV file to begin AI-powered analysis**", icon="🚀")
    st.write("")
    st.write("")
    st.write("")
    
    # Hero tagline with gradient (title is in page config) - BELOW upload
    st.markdown('''
    <div style="text-align: center; padding: 1.5rem 0 2.5rem 0;">
        <p style="font-size: 2rem; 
                   background: linear-gradient(135deg, #818cf8 0%, #6ee7b7 50%, #c4b5fd 100%); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent; 
                   margin-bottom: 0.8rem; 
                   font-weight: 700;
                   letter-spacing: -0.5px;">
            Enterprise-Grade Data Quality & Privacy Platform
        </p>
        <p style="font-size: 1.15rem; color: #94a3b8; font-weight: 500;">
            🤖 AI Analysis • 🔒 Privacy Protection • 📐 Statistical Transformation
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Main feature cards - 3 columns with enhanced styling
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown('''
        <div style="text-align: center; padding: 2.5rem 1.5rem; 
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%); 
                    border-radius: 16px; 
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1);
                    transition: all 0.3s ease;
                    height: 100%;
                    cursor: pointer;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem; transition: transform 0.3s ease;">🤖</div>
            <h3 style="color: #a5b4fc; margin-bottom: 1rem; font-size: 1.3rem;">AI Detection</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                Machine learning finds complex anomalies traditional methods miss
            </p>
        </div>
        <style>
        div[style*="rgba(99, 102, 241"]:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 28px rgba(99, 102, 241, 0.25) !important;
            border-color: rgba(99, 102, 241, 0.6) !important;
        }
        div[style*="rgba(99, 102, 241"]:hover div {
            transform: scale(1.1);
        }
        </style>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div style="text-align: center; padding: 2.5rem 1.5rem; 
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%); 
                    border-radius: 16px; 
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    box-shadow: 0 8px 16px rgba(16, 185, 129, 0.1);
                    transition: all 0.3s ease;
                    height: 100%;
                    cursor: pointer;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem; transition: transform 0.3s ease;">🔒</div>
            <h3 style="color: #6ee7b7; margin-bottom: 1rem; font-size: 1.3rem;">Privacy Shield</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                Enterprise PII detection with GDPR/CCPA compliance
            </p>
        </div>
        <style>
        div[style*="rgba(16, 185, 129"]:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 28px rgba(16, 185, 129, 0.25) !important;
            border-color: rgba(16, 185, 129, 0.6) !important;
        }
        div[style*="rgba(16, 185, 129"]:hover div {
            transform: scale(1.1);
        }
        </style>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div style="text-align: center; padding: 2.5rem 1.5rem; 
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%); 
                    border-radius: 16px; 
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    box-shadow: 0 8px 16px rgba(139, 92, 246, 0.1);
                    transition: all 0.3s ease;
                    height: 100%;
                    cursor: pointer;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem; transition: transform 0.3s ease;">📐</div>
            <h3 style="color: #c4b5fd; margin-bottom: 1rem; font-size: 1.3rem;">Smart Transform</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                6 statistical transformations with auto-recommendations
            </p>
        </div>
        <style>
        div[style*="rgba(139, 92, 246"]:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 28px rgba(139, 92, 246, 0.25) !important;
            border-color: rgba(139, 92, 246, 0.6) !important;
        }
        div[style*="rgba(139, 92, 246"]:hover div {
            transform: scale(1.1);
        }
        </style>
        ''', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # New Features Highlight Banner with enhanced styling
    st.markdown('''
    <style>
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2); }
        50% { box-shadow: 0 8px 32px rgba(99, 102, 241, 0.4); }
    }
    .new-features-banner {
        animation: pulse-glow 3s ease-in-out infinite;
    }
    </style>
    <div class="new-features-banner" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%); 
                padding: 2rem; 
                border-radius: 16px; 
                border: 1px solid rgba(99, 102, 241, 0.4); 
                text-align: center; 
                margin-bottom: 2.5rem;">
        <div style="display: inline-block; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 0.4rem 1rem; 
                    border-radius: 20px; 
                    margin-bottom: 0.8rem;">
            <span style="color: white; font-weight: 600; font-size: 0.85rem; letter-spacing: 1px;">
                🆕 NEW FEATURES
            </span>
        </div>
        <h3 style="color: #a5b4fc; margin-bottom: 0.5rem; font-size: 1.4rem; font-weight: 600;">
            Enterprise Capabilities Just Launched
        </h3>
        <p style="color: #cbd5e1; margin-bottom: 0; font-size: 1rem;">
            Advanced Outlier Treatment • Skewness Correction • PII Protection • Privacy Risk Scoring
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Detailed capabilities - 2 columns with professional styling
    cap_col1, cap_col2 = st.columns(2, gap="large")
    
    with cap_col1:
        st.markdown('''
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%); 
                    padding: 2rem; 
                    border-radius: 14px; 
                    border-left: 4px solid #818cf8; 
                    border-right: 1px solid rgba(129, 140, 248, 0.2);
                    border-top: 1px solid rgba(129, 140, 248, 0.2);
                    border-bottom: 1px solid rgba(129, 140, 248, 0.2);
                    height: 100%;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #818cf8; margin-bottom: 1.2rem; font-size: 1.2rem; font-weight: 600;">
                🛠️ Data Quality & Cleaning
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">5 Outlier Methods:</strong> IQR, Winsorize, Z-score, Log, Square Root
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">6 Transformations:</strong> Box-Cox, Yeo-Johnson, Log, Cube Root & more
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">Smart Wizard:</strong> Step-by-step data cleaning pipeline
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">Auto-Fix:</strong> One-click cleaning with live preview
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">Missing Values:</strong> MICE imputation & intelligent handling
                </li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with cap_col2:
        st.markdown('''
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%); 
                    padding: 2rem; 
                    border-radius: 14px; 
                    border-left: 4px solid #6ee7b7; 
                    border-right: 1px solid rgba(110, 231, 183, 0.2);
                    border-top: 1px solid rgba(110, 231, 183, 0.2);
                    border-bottom: 1px solid rgba(110, 231, 183, 0.2);
                    height: 100%;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #6ee7b7; margin-bottom: 1.2rem; font-size: 1.2rem; font-weight: 600;">
                🔐 Enterprise Privacy Protection
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">8+ PII Types:</strong> Email, SSN, Credit Cards, Phone, IP, Names
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Risk Scoring:</strong> 0-100 privacy risk assessment
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Smart Masking:</strong> Intelligent pattern-based anonymization
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Compliance:</strong> GDPR, CCPA, HIPAA, PCI-DSS guidance
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Export Protected:</strong> Download masked or PII-free datasets
                </li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Analytics capabilities - 2 columns
    analytics_col1, analytics_col2 = st.columns(2, gap="large")
    
    with analytics_col1:
        st.markdown('''
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%); 
                    padding: 2rem; 
                    border-radius: 14px; 
                    border-left: 4px solid #c4b5fd;
                    border-right: 1px solid rgba(196, 181, 253, 0.2);
                    border-top: 1px solid rgba(196, 181, 253, 0.2);
                    border-bottom: 1px solid rgba(196, 181, 253, 0.2);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #c4b5fd; margin-bottom: 1.2rem; font-size: 1.2rem; font-weight: 600;">
                📊 Advanced Analytics
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #c4b5fd;">✓</span> 
                    <strong style="color: #e2e8f0;">AI Anomaly Detection:</strong> Isolation Forest ML algorithms
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #c4b5fd;">✓</span> 
                    <strong style="color: #e2e8f0;">PCA Analysis:</strong> Dimensionality reduction & variance
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #c4b5fd;">✓</span> 
                    <strong style="color: #e2e8f0;">Q-Q Plots:</strong> Normality assessment for transformations
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #c4b5fd;">✓</span> 
                    <strong style="color: #e2e8f0;">Correlation Maps:</strong> Interactive heatmaps & relationships
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #c4b5fd;">✓</span> 
                    <strong style="color: #e2e8f0;">Statistical Profiling:</strong> Deep data characterization
                </li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with analytics_col2:
        st.markdown('''
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%); 
                    padding: 2rem; 
                    border-radius: 14px; 
                    border-left: 4px solid #fbbf24;
                    border-right: 1px solid rgba(251, 191, 36, 0.2);
                    border-top: 1px solid rgba(251, 191, 36, 0.2);
                    border-bottom: 1px solid rgba(251, 191, 36, 0.2);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #fbbf24; margin-bottom: 1.2rem; font-size: 1.2rem; font-weight: 600;">
                💻 Code & Export
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">Full Pipeline Code:</strong> Cleaning, outliers, transformations
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">Reproducible:</strong> Export Python scripts for production
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">Transformation Recipes:</strong> Save and reuse workflows
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">History & Undo:</strong> Track all changes with rollback
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">AI Training Code:</strong> Ready-to-use ML model scripts
                </li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Test dataset button with enhanced styling
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button(
            "🎲 GENERATE TEST DATASET WITH ANOMALIES",
            type="primary",
            width="stretch"
        ):
            sample_df = generate_test_dataset()
            st.success("✅ Test dataset generated! Download below:")
            st.download_button(
                "⬇️ Download Sample CSV",
                sample_df.to_csv(index=False),
                "test_data_with_anomalies.csv",
                "text/csv",
                width="stretch"
            )
    
    st.write("")
    st.write("")
    
    # Quick Start Guide with enhanced styling
    with st.expander("💡 Platform Capabilities & Quick Start Guide", expanded=False):
        st.markdown("""
        ### 🔍 What We Analyze
        
        **Data Quality**
        - Missing value patterns & intelligent imputation
        - Duplicate detection & removal
        - Outlier identification (5 treatment methods)
        - Format consistency validation
        
        **🤖 AI-Powered Insights**
        - MICE imputation analysis
        - Isolation Forest anomaly detection
        - Statistical profiling & correlation analysis
        
        **📐 Distribution Analysis**
        - Skewness detection & normalization (6 methods)
        - Q-Q plots for normality assessment
        - Box-Cox, Yeo-Johnson, Log transforms
        
        **🔒 Privacy & Compliance**
        - Automatic PII detection (8+ types)
        - Privacy risk scoring (0-100 scale)
        - GDPR, CCPA, HIPAA, PCI-DSS guidance
        - One-click data anonymization
        
        ---
        
        ### 📊 12 Analysis Tabs
        
        | Tab | Description |
        |-----|-------------|
        | 📊 **Dashboard** | Analysis history & saved reports |
        | 📋 **Overview** | Health score & key metrics |
        | 🧠 **AI Deep Dive** | ML anomaly detection |
        | 🛠️ **Fix Data** | 5 outlier methods + smart wizard |
        | 📐 **Skewness** 🆕 | 6 transformation methods |
        | 🔧 **Pipeline** | Custom cleaning workflows |
        | 📊 **Visualizations** | Interactive Plotly charts |
        | 📉 **PCA** | Dimensionality reduction |
        | 💻 **Code Export** | Production-ready Python |
        | 🔒 **Deep Profile** 🆕 | PII detection & masking |
        | 📈 **Compare** | Side-by-side analysis |
        | 🎲 **Synthetic Data** | Generate test datasets |
        
        ---
        
        ### 🚀 Quick Workflow
        
        1. **Upload CSV** → Get instant health score
        2. **Review AI Insights** → Identify anomalies & PII
        3. **Fix Data** → Use wizard or manual tools
        4. **Transform Skewness** → Normalize distributions
        5. **Protect Privacy** → Mask or remove PII
        6. **Export Code** → Get Python scripts
        7. **Download** → Cleaned, transformed dataset
        
        ---
        
        ### 💡 Key Features
        
        - **5 Outlier Methods:** IQR, Winsorize, Z-score, Log, √
        - **6 Transformations:** Box-Cox, Yeo-Johnson, Log, Cube Root, √, Reciprocal
        - **8+ PII Types:** Email, SSN, Phone, Credit Card, IP, ZIP, Names, Addresses
        - **Auto-Save:** All analyses saved to dashboard
        - **Reproducible:** Export complete Python code
        - **Compliance Ready:** GDPR, CCPA, HIPAA, PCI-DSS
        """)
    
    # Footer stats with enhanced styling
    st.write("")
    st.write("")
    st.markdown('''
    <style>
    .stat-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .stat-card:hover {
        transform: translateY(-8px) scale(1.05);
        filter: brightness(1.2);
    }
    </style>
    <div style="text-align: center; 
                padding: 2.5rem; 
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(30, 41, 59, 0.3) 100%); 
                border-radius: 16px; 
                border: 1px solid rgba(100, 116, 139, 0.4);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem;">
            <div class="stat-card" style="padding: 1rem; border-radius: 12px; background: rgba(99, 102, 241, 0.1);">
                <h2 style="color: #818cf8; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">12</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">Analysis Tabs</p>
            </div>
            <div class="stat-card" style="padding: 1rem; border-radius: 12px; background: rgba(16, 185, 129, 0.1);">
                <h2 style="color: #6ee7b7; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">11</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">Transform Methods</p>
            </div>
            <div class="stat-card" style="padding: 1rem; border-radius: 12px; background: rgba(251, 191, 36, 0.1);">
                <h2 style="color: #fbbf24; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">8+</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">PII Types Detected</p>
            </div>
            <div class="stat-card" style="padding: 1rem; border-radius: 12px; background: rgba(139, 92, 246, 0.1);">
                <h2 style="color: #c4b5fd; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">100%</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">Free & Open</p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()