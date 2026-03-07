"""
DataForge Studio - Main Application
Enterprise-Grade ML Data Preparation Platform
Multi-format upload • EDA • Cleaning • Skewness • Feature Engineering • Model Building
"""
import streamlit as st
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="DataForge Studio",
    page_icon="⚡",
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

# ✨ EDA Report tab
try:
    from tabs.tab_eda_report import render_eda_tab
    EDA_AVAILABLE = True
except ImportError:
    EDA_AVAILABLE = False
    print("⚠️  EDA tab not found")

# ✨ Model Builder tab
try:
    from tabs.tab_model_builder import render_model_builder_tab
    MODEL_BUILDER_AVAILABLE = True
except ImportError:
    MODEL_BUILDER_AVAILABLE = False
    print("⚠️  Model Builder tab not found")

# ✨ NEW: Import Feature Engineering tab
try:
    from tabs.tab_feature_engineering import render_feature_engineering_tab
    FEATURE_ENGINEERING_AVAILABLE = True
except ImportError:
    # Fallback: use pipeline tab if feature engineering not available
    from tabs.tab_pipeline import render_pipeline_tab as render_feature_engineering_tab
    FEATURE_ENGINEERING_AVAILABLE = False
    print("⚠️  Feature Engineering tab not found, using pipeline tab")

from tabs.tab_imbalanced import render_imbalanced_tab
from tabs.tab_pca import render_pca_tab
from tabs.tab_code import render_code_tab
from tabs.tab_deep_profile import render_deep_profile_tab
from tabs.tab_synthetic import render_synthetic_tab
from tabs.tab_dashboard import render_dashboard_tab

# Import export utilities
from export.pdf_generator import generate_pdf
from visualization.charts import render_overview_metrics, render_dataset_overview_cards

# Import database functions
from database.db_functions import save_analysis

# ✨ NEW: Import utility functions
try:
    from utils.pipeline_code_generator import generate_complete_pipeline_code, show_pipeline_summary
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("⚠️  Utils not found, some features will be disabled")

import time


def main():
    """Main application flow"""
    # 1. Setup page configuration
    setup_page_config()
    
    # 2. Load custom CSS
    load_custom_css()
    
    # ═══════════════════════════════════════════════════════════════════════
    # ✨ ENHANCED CSS WITH HOVER EFFECTS AND ANIMATIONS
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Enhanced file uploader styling */
    /* ═══════════════════════════════════════════════════════════════════ */
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
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* ✨ ENHANCED TAB HOVER EFFECTS - CLEANER & MORE COMPACT */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    /* Tab container styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        padding: 4px;
        border-radius: 0;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Individual tab styling */
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: rgba(203, 213, 224, 0.6);
        font-weight: 500;
        font-size: 13px;
        padding: 0 16px;
        border: none;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
        position: relative;
    }
    
    /* Tab hover state */
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.08);
        color: rgba(226, 232, 240, 0.9);
        border-bottom: 2px solid rgba(99, 102, 241, 0.4);
    }
    
    /* Active/selected tab */
    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.12);
        color: #ffffff !important;
        border-bottom: 2px solid #6366f1;
        font-weight: 600;
    }
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Enhanced button styling */
    /* ═══════════════════════════════════════════════════════════════════ */
    .stButton > button {
        transition: all 0.3s ease !important;
        border-radius: 12px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Primary button glow */
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Card hover effects */
    /* ═══════════════════════════════════════════════════════════════════ */
    .stMarkdown div[style*="border-radius"] {
        transition: all 0.3s ease;
    }
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Smooth scroll behavior */
    /* ═══════════════════════════════════════════════════════════════════ */
    html {
        scroll-behavior: smooth;
    }
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Expander hover effect */
    /* ═══════════════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(99, 102, 241, 0.05) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Metric card animations */
    /* ═══════════════════════════════════════════════════════════════════ */
    [data-testid="stMetric"] {
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
    }
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* Download button special effects */
    /* ═══════════════════════════════════════════════════════════════════ */
    .stDownloadButton > button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 3. Show user info in sidebar
    show_user_info_sidebar()
    
    # 4. Render sidebar and get settings
    settings = render_sidebar()
    
    # 5. Render hero section
    render_hero_section()
       
    # 6. File upload - UPDATED TO SUPPORT MULTIPLE FORMATS
    uploaded_file = st.file_uploader(
        "📂 Drop your data file here or click to browse",
        type=['csv', 'tsv', 'txt', 'xlsx', 'xls', 'json', 'parquet', 'feather', 'orc'],
        help="Supported: CSV, TSV, TXT, Excel, JSON, Parquet, Feather, ORC"
    )
    
    # 7. Handle file upload or show landing page
    if uploaded_file:
        # ✨ NEW: Mark that data has been uploaded
        st.session_state['data_uploaded'] = True
        
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
        # ══════════════════════════════════════════════════════════
        # TAB LAYOUT
        # Flow: Dashboard → Overview → EDA → Fix Data → Skewness
        #       → Feature Eng → Model Builder → Visualizations
        #       → PCA → Code → Deep Profile → Compare → Synthetic
        # ══════════════════════════════════════════════════════════
        (
            tab0, tab1, tab2,
            tab3, tab4, tab5,
            tab6, tab7, tab8,
            tab9, tab10, tab11,
            tab12
        ) = st.tabs([
            "📊 Dashboard",
            "📋 Overview",
            "🧠 AI Deep Dive",

            "🛠️ Fix Data",
            "📈 EDA Report",
            "📐 Skewness",

            "🔧 Feature Engineering",
            "🤖 Model Builder",
            "⚖️ Imbalanced Data",

            "📉 PCA",
            "💻 Code",
            "🔒 Deep Profile",
            "🎲 Synthetic Data",
        ])

        # ── OVERVIEW GROUP ───────────────────────────────────────
        with tab0:
            render_dashboard_tab()

        with tab1:
            render_overview_tab(df, results, col_types)

        with tab2:
            render_ai_deep_dive_tab(df, results, col_types, settings)

        # ── DATA PREP PIPELINE ───────────────────────────────────
        with tab3:
            render_fix_data_tab(df, results, col_types, settings)

        with tab4:
            # EDA — always run on best available df
            eda_df = df
            if st.session_state.get('anomaly_cleaned_df') is not None:
                eda_df = st.session_state['anomaly_cleaned_df']
            if st.session_state.get('global_cleaned_df') is not None:
                eda_df = st.session_state['global_cleaned_df']
            if st.session_state.get('skew_fixed_df') is not None:
                eda_df = st.session_state['skew_fixed_df']
            if st.session_state.get('engineered_df') is not None:
                eda_df = st.session_state['engineered_df']
            
            eda_col_types = {
                'numeric':     eda_df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical': eda_df.select_dtypes(include=['object','category']).columns.tolist(),
                'datetime':    eda_df.select_dtypes(include=['datetime64']).columns.tolist(),
            }
            if EDA_AVAILABLE:
                render_eda_tab(eda_df, eda_col_types)
            else:
                st.info("📈 EDA Report tab not found. Add `tabs/tab_eda_report.py` to enable.")

        with tab5:
            skew_df = df
            if st.session_state.get('anomaly_cleaned_df') is not None:
                skew_df = st.session_state['anomaly_cleaned_df']
            if st.session_state.get('global_cleaned_df') is not None:
                skew_df = st.session_state['global_cleaned_df']
            if st.session_state.get('skew_fixed_df') is not None:
                skew_df = st.session_state['skew_fixed_df']
            render_skewness_tab(skew_df, settings)

        # ── ML PREP ──────────────────────────────────────────────
        with tab6:
            render_feature_engineering_tab(df, col_types)

        
         # tab7 = Model Builder 
        with tab7:
            model_df = df
            for key in ['balanced_df', 'engineered_df', 'skew_fixed_df', 'anomaly_cleaned_df', 'global_cleaned_df']:
                if st.session_state.get(key) is not None:
                    model_df = st.session_state[key]
                    break
            model_col_types = {
                'numeric':     model_df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical': model_df.select_dtypes(include=['object','category']).columns.tolist(),
                'datetime':    model_df.select_dtypes(include=['datetime64']).columns.tolist(),
            }
            if MODEL_BUILDER_AVAILABLE:
                render_model_builder_tab(model_df, model_col_types)
            else:
                st.info("🤖 Model Builder tab not found.")

        # tab8 = Imbalanced Data (moved down)
        with tab8:
            imb_df = df
            for key in ['engineered_df', 'skew_fixed_df', 'anomaly_cleaned_df', 'global_cleaned_df']:
                if st.session_state.get(key) is not None:
                    imb_df = st.session_state[key]
                    break
            imb_col_types = {
                'numeric':     imb_df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical': imb_df.select_dtypes(include=['object','category']).columns.tolist(),
                'datetime':    imb_df.select_dtypes(include=['datetime64']).columns.tolist(),
            }
            render_imbalanced_tab(imb_df, imb_col_types)

            # tab9 = PCA 
        with tab9:
            pca_df = df
            for key in ['engineered_df', 'skew_fixed_df', 'global_cleaned_df', 'anomaly_cleaned_df']:
                if st.session_state.get(key) is not None:
                    pca_df = st.session_state[key]
                    break
            pca_col_types = {
                'numeric':     pca_df.select_dtypes(include=[np.number]).columns.tolist(),
                'categorical': pca_df.select_dtypes(include=['object','category']).columns.tolist(),
                'datetime':    pca_df.select_dtypes(include=['datetime64']).columns.tolist(),
            }
            render_pca_tab(pca_df, results, pca_col_types,settings)

        # ── EXPORT / ADVANCED ────────────────────────────────────
        with tab10:
            if UTILS_AVAILABLE:
                st.subheader("💻 Code Generation")
                code_tab1, code_tab2 = st.tabs([
                    "📦 Complete Pipeline (Production)",
                    "🔧 Individual Scripts (Development)"
                ])
                with code_tab1:
                    st.markdown("### 📦 Production-Ready Pipeline")
                    st.caption(
                        "Single Python script combining all transformations. "
                        "**Users can complete tabs in any order!**"
                    )
                    show_pipeline_summary()
                    st.markdown("---")
                    complete_code = generate_complete_pipeline_code()
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            "📥 Download Complete Pipeline",
                            data=complete_code,
                            file_name="complete_pipeline.py",
                            mime="text/plain",
                            type="primary"
                        )
                    with c2:
                        st.metric("Lines of Code", len(complete_code.split('\n')))
                    with st.expander("👁️ Preview", expanded=True):
                        st.code(complete_code, language='python')
                with code_tab2:
                    render_code_tab(col_types, settings)
            else:
                render_code_tab(col_types, settings)

        with tab11:
            render_deep_profile_tab(df)

        with tab12:
            render_synthetic_tab(df, col_types)

        # ══════════════════════════════════════════════════════════
        # BOTTOM EXPORT BAR — always shows most-processed data
        # ══════════════════════════════════════════════════════════
        st.markdown("---")

        export_df = df
        export_label = "Original"
        
        if st.session_state.get('anomaly_cleaned_df') is not None:
            export_df = st.session_state['anomaly_cleaned_df']
            export_label = "Anomaly-Free"
        if st.session_state.get('global_cleaned_df') is not None:
            export_df = st.session_state['global_cleaned_df']
            export_label = "Cleaned"
        if st.session_state.get('skew_fixed_df') is not None:
            export_df = st.session_state['skew_fixed_df']
            export_label = "Skewness Corrected"
        if st.session_state.get('engineered_df') is not None:
            export_df = st.session_state['engineered_df']
            export_label = "Feature Engineered"

        col_pdf, col_data, col_code = st.columns(3)

        with col_pdf:
            st.download_button(
                "📄 Download PDF Report",
                generate_pdf(df, results),
                "ai_health_report.pdf",
                "application/pdf"
            )

        with col_data:
            from utils.export_utils import smart_download_button
            smart_download_button(
                export_df,
                label=f"📊 Download {export_label} Data",
                suffix=export_label.lower().replace(' ', '_'),
                key="dl_bottom_export"
            )

        with col_code:
            if UTILS_AVAILABLE:
                complete_code = generate_complete_pipeline_code()
                st.download_button(
                    "💻 Download Complete Code",
                    data=complete_code,
                    file_name="complete_pipeline.py",
                    mime="text/plain"
                )
            else:
                summary_data = (
                    results['stats']['missing_info'].to_csv(index=False)
                    if not results['stats']['missing_info'].empty
                    else "No issues found"
                )
                st.download_button(
                    "📊 Download Summary",
                    summary_data,
                    "analysis_summary.csv",
                    "text/csv"
                )
    
    else:
        # Landing page
        render_landing_page()


def render_landing_page():
    """Render enhanced professional landing page with hover effects"""
    
    # Hero tagline with gradient (title is in page config)
    st.markdown('''
    <div style="text-align: center; padding: 1.5rem 0 2.5rem 0;">
        <p style="font-size: 2rem; 
                   background: linear-gradient(135deg, #818cf8 0%, #6ee7b7 50%, #c4b5fd 100%); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent; 
                   margin-bottom: 0.8rem; 
                   font-weight: 700;
                   letter-spacing: -0.5px;">
            End-to-End ML Data Preparation Platform
        </p>
        <p style="font-size: 1.15rem; color: #94a3b8; font-weight: 500;">
            📈 EDA • 🛠️ Cleaning • 📐 Skewness • 🔧 Feature Eng • 🤖 Model Building
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.info("👆 **Upload CSV, TSV, Excel, Parquet, JSON or other formats to begin**", icon="🚀")
    st.write("")
    
    # Main feature cards - 3 columns with enhanced styling AND HOVER EFFECTS
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown('''
        <div style="text-align: center; padding: 2.5rem 1.5rem; 
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%); 
                    border-radius: 16px; 
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.1);
                    transition: transform 0.3s ease;
                    height: 100%;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">🛠️</div>
            <h3 style="color: #a5b4fc; margin-bottom: 1rem; font-size: 1.3rem;">Smart Cleaning</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                AI-powered data cleaning with MICE imputation, 5 outlier methods & step-by-step wizard
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
                    transition: transform 0.3s ease;
                    height: 100%;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: #6ee7b7; margin-bottom: 1rem; font-size: 1.3rem;">Model Builder</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                Train 12 ML algorithms with visual train/test split, cross-validation & feature importance
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
                    transition: transform 0.3s ease;
                    height: 100%;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">📦</div>
            <h3 style="color: #c4b5fd; margin-bottom: 1rem; font-size: 1.3rem;">9 File Formats</h3>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">
                Upload & download in CSV, TSV, Excel, Parquet, JSON, Feather, ORC and more
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
    
    # New Features Highlight Banner with enhanced styling AND PULSE GLOW
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
            Complete End-to-End ML Platform
        </h3>
        <p style="color: #cbd5e1; margin-bottom: 0; font-size: 1rem;">
            EDA Report • Model Builder • 9 File Formats • Train/Test Split • Feature Engineering • PII Protection
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
                    <strong style="color: #e2e8f0;">6 Skewness Fixes:</strong> Box-Cox, Yeo-Johnson, Log, Cube Root & more
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">Smart Wizard:</strong> Step-by-step data cleaning pipeline
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">Auto-Fix:</strong> AI-powered one-click cleaning with live preview
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #818cf8;">✓</span> 
                    <strong style="color: #e2e8f0;">MICE Imputation:</strong> Multivariate intelligent missing value handling
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
                🤖 ML & Feature Engineering
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">12 Algorithms:</strong> Random Forest, XGBoost, SVM, KNN & more
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Visual Split:</strong> Train/test split with class balance preview
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Feature Engineering:</strong> Scaling, encoding, polynomial & power transforms
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Auto Quick Setup:</strong> One-click ML configuration
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #6ee7b7;">✓</span> 
                    <strong style="color: #e2e8f0;">Export Model:</strong> Download trained model + pipeline code
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
                📊 Advanced Analytics & EDA
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #c4b5fd;">✓</span> 
                    <strong style="color: #e2e8f0;">EDA Report:</strong> Quality scoring, alerts & correlation analysis
                </li>
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
                💻 Code, Export & Privacy
            </h4>
            <ul style="color: #cbd5e1; font-size: 0.95rem; line-height: 2; list-style: none; padding-left: 0;">
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">9 Formats:</strong> CSV, TSV, Excel, Parquet, JSON, Feather, ORC
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">Full Pipeline Code:</strong> Auto-generated production Python script
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">8+ PII Types:</strong> Email, SSN, Credit Cards, Phone, IP & more
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">Privacy Shield:</strong> GDPR, CCPA, HIPAA, PCI-DSS guidance
                </li>
                <li style="margin-bottom: 0.5rem;">
                    <span style="color: #fbbf24;">✓</span> 
                    <strong style="color: #e2e8f0;">Smart Download:</strong> Always downloads in your original format
                </li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Test dataset button
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button(
            "🎲 GENERATE COMPREHENSIVE TEST DATASET",
            type="primary"
        ):
            sample_df = generate_test_dataset()
            st.success("✅ Test dataset generated! Includes: imbalanced classes, outliers, missing values, skewed data, and PII")
            st.download_button(
                "⬇️ Download Test Dataset (CSV)",
                sample_df.to_csv(index=False),
                "dataforge_test_dataset.csv",
                "text/csv"
            )
    
    st.write("")
    st.write("")
    
    # Quick Start Guide with enhanced styling
    with st.expander("💡 What's in DataForge Studio", expanded=False):
        st.markdown("""
        ### ✨ Full Feature Set
        
        **📦 9 File Formats — Upload & Download**
        - CSV, TSV, TXT, Excel (.xlsx/.xls), JSON, Parquet, Feather, ORC
        - Every download button returns your **original format** automatically
        - Smart encoding detection, datetime auto-detection, column sanitization
        
        **🛠️ Fix Data — 5 Outlier Methods**
        - IQR removal, Winsorize (cap), Z-score, Log transform, Square Root
        - Smart Wizard: guided step-by-step cleaning pipeline
        - AI Auto-Repair: one-click cleaning with live preview
        - MICE imputation for missing values
        - Manual editor with full control
        
        **📐 Skewness — 6 Transformation Methods**
        - Log, Square Root, Cube Root, Box-Cox, Yeo-Johnson, Reciprocal
        - Q-Q plots for normality assessment
        - Single column, bulk transform, and transformation history
        
        **🔧 Feature Engineering**
        - Scaling: Standard, MinMax, Robust (with before/after preview)
        - Encoding: One-Hot, Label Encoding
        - Advanced: Normalization, Power Transform, Quantile, Polynomial Features
        - Box-Cox validation, polynomial count warnings, Quick ML Setup
        
        **🤖 Model Builder — 12 Algorithms**
        - Classification & Regression support
        - Visual train/test split with class balance preview & imbalance warning
        - Stratified split, cross-validation, random seed control
        - Algorithms: Random Forest, Gradient Boosting, Logistic/Linear Regression,
          Ridge, Lasso, SVM, Decision Tree, KNN and more
        - Feature importance, confusion matrix, ROC curve, metrics export
        
        **⚖️ Imbalanced Data Handler**
        - SMOTE & ADASYN synthetic oversampling (pure NumPy implementation)
        - Random undersampling for large datasets
        - Class weight balancing for sklearn models
        - Automatic imbalance detection with severity scoring
        - Before/after class distribution charts
        
        **🔒 Privacy & Compliance**
        - 8+ PII types: Email, SSN, Credit Cards, Phone, IP, ZIP, Names, Addresses
        - 0-100 privacy risk scoring
        - Smart masking & anonymization
        - GDPR, CCPA, HIPAA, PCI-DSS guidance
        
        ---
        
        ### 📊 13 Analysis Tabs
        
        | Tab | Description |
        |-----|-------------|
        | 📊 **Dashboard** | Analysis history & saved reports |
        | 📋 **Overview** | Health score & key metrics |
        | 🧠 **AI Deep Dive** | ML anomaly detection |
        | 📈 **EDA Report** | Quality scoring, smart alerts, correlation |
        | 🛠️ **Fix Data** | 5 outlier methods + MICE + smart wizard |
        | 📐 **Skewness** | 6 transformation methods + Q-Q plots |
        | 🔧 **Feature Engineering** | Scaling, encoding & advanced transforms |
        | 🤖 **Model Builder** | 12 algorithms, train/test split, metrics |
        | ⚖️ **Imbalanced Data** | SMOTE, ADASYN for class imbalance |
        | 📉 **PCA** | Dimensionality reduction |
        | 💻 **Code** | Production-ready Python + individual scripts |
        | 🔒 **Deep Profile** | PII detection & masking |
        | 🎲 **Synthetic Data** | Generate test datasets |
        
        ---
        
        ### 🚀 Recommended Workflow
        
        1. **Upload your file** (CSV, Excel, Parquet, JSON etc.) → instant health score
        2. **EDA Report** → understand distributions, correlations, quality
        3. **AI Deep Dive** → identify anomalies & PII risks
        4. **Fix Data** → wizard or manual cleaning, MICE imputation
        5. **Skewness** → normalize distributions with 6 methods
        6. **Feature Engineering** → scale, encode & transform for ML
        7. **Model Builder** → train model & check performance
        8. **Imbalanced Data** → fix class imbalance if accuracy is poor (optional)
        9. **Deep Profile** → mask or remove PII before sharing
        10. **Code tab** → download complete reproducible pipeline
        11. **Download** → in your original file format
        
        ---
        
        ### 💡 Key Numbers
        
        - **12 ML algorithms** (classification & regression)
        - **9 file formats** supported for upload & download
        - **5 outlier treatment** methods
        - **6 skewness transformations**
        - **7+ feature engineering** operations
        - **8+ PII types** detected
        - **13 analysis tabs**
        - **100% free** — no limits, no account required
        """)
    
    # Footer stats with enhanced styling AND HOVER ANIMATION
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
                <h2 style="color: #818cf8; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">13</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">Analysis Tabs</p>
            </div>
            <div class="stat-card" style="padding: 1rem; border-radius: 12px; background: rgba(16, 185, 129, 0.1);">
                <h2 style="color: #6ee7b7; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">12</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">ML Algorithms</p>
            </div>
            <div class="stat-card" style="padding: 1rem; border-radius: 12px; background: rgba(251, 191, 36, 0.1);">
                <h2 style="color: #fbbf24; margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 700;">9</h2>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">File Formats</p>
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