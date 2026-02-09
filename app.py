"""
Smart CSV Health Checker AI - Main Application
Entry point for the Streamlit app
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
from tabs.tab_skewness import render_skewness_tab  # ✅ NEW: Skewness Analysis
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
        
        # ==================== RENDER TABS (UPDATED WITH SKEWNESS) ====================
        tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
            "📊 Dashboard",
            "📋 Overview",
            "🧠 AI Deep Dive",
            "🛠️ Fix Data",
            "📐 Skewness",        # ✅ NEW: Positioned after Fix Data
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
            current_df = st.session_state.get('global_cleaned_df')
            if current_df is None:
                current_df = st.session_state.get('skew_fixed_df')
            if current_df is None:
                current_df = df
            render_skewness_tab(current_df, settings)
        
        with tab5:
            render_pipeline_tab(df)
        
        with tab6:
            viz_df = st.session_state.get('skew_fixed_df')
            if viz_df is None:
                viz_df = st.session_state.get('global_cleaned_df')
            if viz_df is None:
                viz_df = df
            render_visualizations_tab(viz_df, col_types, results)
        
        with tab7:
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
                use_container_width=True
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
                use_container_width=True
            )
    
    else:
        # Landing page
        render_landing_page()


def render_landing_page():
    """Render enhanced landing page when no file is uploaded"""
    
    # Hero section
    st.markdown('''
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
        <h1 style="font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   margin-bottom: 1rem; font-weight: 800;">
            Smart CSV AI Studio
        </h1>
        <p style="font-size: 1.3rem; color: #94a3b8; margin-bottom: 0.5rem;">
            Enterprise-Grade Data Quality & Privacy Platform
        </p>
        <p style="font-size: 1rem; color: #64748b;">
            AI-Powered Analysis • Privacy Protection • Statistical Transformation
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.info("👆 Upload a CSV file to begin AI-powered analysis")
    st.write("")
    
    # Main feature cards - 3 columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: rgba(99, 102, 241, 0.1); 
                    border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: #a5b4fc; margin-bottom: 1rem;">AI Detection</h3>
            <p style="color: #94a3b8; font-size: 0.95rem;">Machine learning finds complex anomalies traditional methods miss</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: rgba(16, 185, 129, 0.1); 
                    border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔒</div>
            <h3 style="color: #6ee7b7; margin-bottom: 1rem;">Privacy Shield</h3>
            <p style="color: #94a3b8; font-size: 0.95rem;">Enterprise PII detection & GDPR/CCPA compliance</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: rgba(139, 92, 246, 0.1); 
                    border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.2);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📐</div>
            <h3 style="color: #c4b5fd; margin-bottom: 1rem;">Smart Transform</h3>
            <p style="color: #94a3b8; font-size: 0.95rem;">6 statistical transformations with auto-recommendations</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # New Features Highlight Banner
    st.markdown('''
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%); 
                padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.3); 
                text-align: center; margin-bottom: 2rem;">
        <h3 style="color: #a5b4fc; margin-bottom: 0.5rem;">🆕 New Enterprise Features</h3>
        <p style="color: #cbd5e1; margin-bottom: 0;">
            Advanced Outlier Treatment • Skewness Correction • PII Protection • Privacy Risk Scoring
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Detailed capabilities - 2 columns
    cap_col1, cap_col2 = st.columns(2)
    
    with cap_col1:
        st.markdown('''
        <div style="background: rgba(30, 41, 59, 0.5); padding: 1.5rem; border-radius: 10px; 
                    border-left: 4px solid #667eea; height: 100%;">
            <h4 style="color: #818cf8; margin-bottom: 1rem;">🛠️ Data Quality & Cleaning</h4>
            <ul style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>5 Outlier Methods:</strong> IQR, Winsorize, Z-score, Log, Square Root</li>
                <li><strong>6 Transformations:</strong> Box-Cox, Yeo-Johnson, Log, Cube Root & more</li>
                <li><strong>Smart Wizard:</strong> Step-by-step data cleaning pipeline</li>
                <li><strong>Auto-Fix:</strong> One-click cleaning with live preview</li>
                <li><strong>Missing Values:</strong> MICE imputation & intelligent handling</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with cap_col2:
        st.markdown('''
        <div style="background: rgba(30, 41, 59, 0.5); padding: 1.5rem; border-radius: 10px; 
                    border-left: 4px solid #10b981; height: 100%;">
            <h4 style="color: #6ee7b7; margin-bottom: 1rem;">🔐 Enterprise Privacy Protection</h4>
            <ul style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>8+ PII Types:</strong> Email, SSN, Credit Cards, Phone, IP, Names</li>
                <li><strong>Risk Scoring:</strong> 0-100 privacy risk assessment</li>
                <li><strong>Smart Masking:</strong> Intelligent pattern-based anonymization</li>
                <li><strong>Compliance:</strong> GDPR, CCPA, HIPAA, PCI-DSS guidance</li>
                <li><strong>Export Protected:</strong> Download masked or PII-free datasets</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    
    # Analytics capabilities
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        st.markdown('''
        <div style="background: rgba(30, 41, 59, 0.5); padding: 1.5rem; border-radius: 10px; 
                    border-left: 4px solid #8b5cf6;">
            <h4 style="color: #c4b5fd; margin-bottom: 1rem;">📊 Advanced Analytics</h4>
            <ul style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>AI Anomaly Detection:</strong> Isolation Forest ML algorithms</li>
                <li><strong>PCA Analysis:</strong> Dimensionality reduction & variance</li>
                <li><strong>Q-Q Plots:</strong> Normality assessment for transformations</li>
                <li><strong>Correlation Maps:</strong> Interactive heatmaps & relationships</li>
                <li><strong>Statistical Profiling:</strong> Deep data characterization</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with analytics_col2:
        st.markdown('''
        <div style="background: rgba(30, 41, 59, 0.5); padding: 1.5rem; border-radius: 10px; 
                    border-left: 4px solid #f59e0b;">
            <h4 style="color: #fbbf24; margin-bottom: 1rem;">💻 Code & Export</h4>
            <ul style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
                <li><strong>Full Pipeline Code:</strong> Cleaning, outliers, transformations</li>
                <li><strong>Reproducible:</strong> Export Python scripts for production</li>
                <li><strong>Transformation Recipes:</strong> Save and reuse workflows</li>
                <li><strong>History & Undo:</strong> Track all changes with rollback</li>
                <li><strong>AI Training Code:</strong> Ready-to-use ML model scripts</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Test dataset button
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button(
            "🎲 GENERATE TEST DATASET WITH ANOMALIES",
            type="primary",
            use_container_width=True
        ):
            sample_df = generate_test_dataset()
            st.success("✅ Test dataset generated! Download below:")
            st.download_button(
                "⬇️ Download Sample CSV",
                sample_df.to_csv(index=False),
                "test_data_with_anomalies.csv",
                "text/csv",
                use_container_width=True
            )
    
    st.write("")
    st.write("")
    
    # Quick tips
    with st.expander("💡 Quick Start Guide", expanded=False):
        st.markdown("""
        ### 📤 Upload Requirements
        - **Format:** CSV files only
        - **Size:** Optimized for files < 100MB (handles larger files too)
        - **Data:** Automatically handles missing values, mixed types, and anomalies
        
        ### 🎯 What We Analyze
        
        **🔍 Data Quality**
        - Missing value patterns & intelligent imputation
        - Duplicate detection & removal
        - Format consistency validation
        - Range and constraint checking
        
        **🤖 AI-Powered Insights**
        - MICE imputation analysis
        - Isolation Forest anomaly detection
        - Hidden pattern discovery
        - Predictive quality metrics
        
        **📐 Statistical Analysis**
        - Skewness detection (threshold > 1.0)
        - Automatic transformation recommendations
        - Q-Q plots for normality assessment
        - Distribution analysis with before/after comparison
        
        **🔒 Privacy & Compliance**
        - Automatic PII detection (Email, SSN, Phone, Credit Cards, IP, Names, etc.)
        - Privacy risk scoring (0-100 scale)
        - GDPR, CCPA, HIPAA, PCI-DSS compliance guidance
        - One-click data anonymization
        
        **🛠️ Advanced Features**
        - 5 outlier treatment methods (IQR, Winsorize, Z-score, Log, √)
        - 6 transformation methods (Box-Cox, Yeo-Johnson, Log, Cube Root, √, Reciprocal)
        - Bulk transformation with progress tracking
        - Transformation history with undo capability
        - Recipe export for reproducibility
        
        ### 📊 12 Powerful Tabs
        
        1. **Dashboard** - Analysis history & saved reports
        2. **Overview** - Health score (A-F grading)
        3. **AI Deep Dive** - ML anomaly detection
        4. **Fix Data** - Smart cleaning wizard + 5 outlier methods
        5. **Skewness** - 🆕 Complete transformation suite
        6. **Pipeline** - Custom cleaning workflows
        7. **Visualizations** - Interactive Plotly charts
        8. **PCA** - Dimensionality reduction
        9. **Code Export** - Python scripts for all operations
        10. **Deep Profile** - 🆕 PII detection & privacy protection
        11. **Compare** - Side-by-side dataset analysis
        12. **Synthetic Data** - Generate realistic test data
        
        ### 🚀 Quick Workflow
        
        1. **Upload CSV** → Get instant health score
        2. **Review AI Insights** → Identify anomalies & PII
        3. **Fix Data** → Use Smart Wizard or manual tools
        4. **Transform Skewness** → Auto-recommendations for normality
        5. **Protect Privacy** → Mask or remove PII
        6. **Export Code** → Get production-ready Python scripts
        7. **Download** → Cleaned, transformed, privacy-safe dataset
        
        ### 💾 Auto-Save Features
        - All analyses automatically saved to your dashboard
        - Transformation history tracked with timestamps
        - Session state preserved across tabs
        - One-click access to previous work
        """)
    
    # Footer stats
    st.write("")
    st.write("")
    st.markdown('''
    <div style="text-align: center; padding: 2rem; background: rgba(30, 41, 59, 0.3); 
                border-radius: 10px; border: 1px solid rgba(100, 116, 139, 0.3);">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem;">
            <div>
                <h2 style="color: #818cf8; margin-bottom: 0.5rem;">12</h2>
                <p style="color: #94a3b8; font-size: 0.9rem;">Analysis Tabs</p>
            </div>
            <div>
                <h2 style="color: #6ee7b7; margin-bottom: 0.5rem;">11</h2>
                <p style="color: #94a3b8; font-size: 0.9rem;">Transformation Methods</p>
            </div>
            <div>
                <h2 style="color: #fbbf24; margin-bottom: 0.5rem;">8+</h2>
                <p style="color: #94a3b8; font-size: 0.9rem;">PII Types Detected</p>
            </div>
            <div>
                <h2 style="color: #c4b5fd; margin-bottom: 0.5rem;">100%</h2>
                <p style="color: #94a3b8; font-size: 0.9rem;">Free & Open</p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()