"""
Smart CSV Health Checker AI - Main Application
Entry point for the Streamlit app
"""
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

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
from tabs.tab_pipeline import render_pipeline_tab
from tabs.tab_visualizations import render_visualizations_tab
from tabs.tab_pca import render_pca_tab
from tabs.tab_code import render_code_tab
from tabs.tab_deep_profile import render_deep_profile_tab
from tabs.tab_compare import render_compare_tab
from tabs.tab_synthetic import render_synthetic_tab  # ✅ FIXED: Changed from tab_synthetic_data

# Import export utilities
from export.pdf_generator import generate_pdf
from visualization.charts import render_overview_metrics, render_dataset_overview_cards

import time


def main():
    """Main application flow"""
    # 1. Setup page configuration
    setup_page_config()
    
    # 2. Load custom CSS
    load_custom_css()
    
    # 3. Render sidebar and get settings
    settings = render_sidebar()
    
    # 4. Render hero section
    render_hero_section()
    
    # 5. File upload
    uploaded_file = st.file_uploader(
        "📂 Drop your CSV file here or click to browse",
        type=['csv']
    )
    
    # 6. Handle file upload or show landing page
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
        
        # Display metrics
        st.markdown("---")
        render_overview_metrics(df, results, col_types)
        st.write("##")
        
        # Render tabs with new Synthetic Data tab
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
            "📋 Overview",
            "🧠 AI Deep Dive",
            "🛠️ Fix Data",
            "🔧 Pipeline",
            "📊 Visualizations",
            "📉 PCA",
            "💻 Code",
            "🔒 Deep Profile",
            "📈 Compare",
            "🎲 Synthetic Data"
        ])
        
        with tab1:
            render_overview_tab(df, results, col_types)
        
        with tab2:
            render_ai_deep_dive_tab(df, results, col_types, settings)
        
        with tab3:
            render_fix_data_tab(df, results, col_types)
        
        with tab4:
            render_pipeline_tab(df)
        
        with tab5:
            render_visualizations_tab(df, col_types, results)
        
        with tab6:
            render_pca_tab(df, results, col_types)
        
        with tab7:
            render_code_tab(col_types, settings)
        
        with tab8:
            render_deep_profile_tab(df)
        
        with tab9:
            render_compare_tab(df)
        
        with tab10:
            render_synthetic_tab(df, col_types)  # ✅ FIXED: Changed from render_synthetic_data_tab
        
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
    """Render landing page when no file is uploaded"""
    st.info("👆 Upload a CSV file to begin AI-powered analysis")
    st.write("")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: rgba(99, 102, 241, 0.1); border-radius: 12px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: #a5b4fc;">AI Detection</h3>
            <p style="color: #94a3b8;">Machine learning finds complex anomalies traditional methods miss</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: rgba(16, 185, 129, 0.1); border-radius: 12px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #6ee7b7;">Deep Analytics</h3>
            <p style="color: #94a3b8;">PCA, correlations, and comprehensive statistics</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div style="text-align: center; padding: 2rem; background: rgba(139, 92, 246, 0.1); border-radius: 12px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
            <h3 style="color: #c4b5fd;">Auto-Fix</h3>
            <p style="color: #94a3b8;">One-click cleaning with exportable Python code</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Test dataset button
    st.write("")
    st.write("")
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button(
            "🎲 Generate Test Dataset with Anomalies",
            type="primary",
            use_container_width=True
        ):
            sample_df = generate_test_dataset()
            st.download_button(
                "⬇️ Download Sample CSV",
                sample_df.to_csv(index=False),
                "test_data_with_anomalies.csv",
                "text/csv",
                use_container_width=True
            )
    
    # Quick tips
    st.write("")
    st.write("")
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **Upload Requirements:**
        - CSV files only
        - Any size (optimized for files < 100MB)
        - Handles missing values automatically
        
        **What We Analyze:**
        - 🔍 Missing values and patterns
        - 🤖 AI-powered anomaly detection (MICE imputation)
        - 📊 Statistical distributions
        - 🔗 Correlations and relationships
        - 📉 Dimensionality (PCA)
        - 🔒 PII (Personal Identifiable Information) detection
        - 🎲 Synthetic data generation
        
        **Features:**
        - One-click data fixes
        - Interactive visualizations
        - Exportable Python code
        - PDF reports
        - Compare multiple datasets
        """)


if __name__ == "__main__":
    main()