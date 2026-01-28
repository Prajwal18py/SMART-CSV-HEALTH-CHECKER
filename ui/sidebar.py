"""
Sidebar Component
Settings and configuration options
"""
import streamlit as st


def render_sidebar():
    """
    Render sidebar with app settings
    
    Returns:
        Dictionary with user settings
    """
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.markdown("---")
        
        # AI Sensitivity
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
        
        st.markdown("---")
        
        # Imputation Method
        st.markdown("### 🔧 Imputation Method")
        imputation_display = st.selectbox(
            "Missing Value Imputation",
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
            It's more sophisticated than simple mean/median imputation.
            """)
        
        st.markdown("---")
        
        # Visualization options
        st.markdown("### 📊 Visualization")
        show_3d_pca = st.checkbox(
            "Enable 3D PCA",
            value=False,
            help="Show PCA results in 3D (requires 3+ numeric columns)"
        )
        
        st.markdown("---")
        
        # Export options
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
        
        st.markdown("---")
        
        # Advanced options
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
                "PCA Components",
                min_value=2,
                max_value=10,
                value=3,
                help="Number of principal components for PCA"
            )
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Smart CSV Health Checker AI**
            
            Version: 2.0
            
            **New Features:**
            - 🎲 Synthetic Data Generation
            - 🔒 PII Detection & Anonymization
            - 🤖 MICE Imputation (Advanced)
            
            **Previous Features:**
            - AI-powered anomaly detection
            - Comprehensive data profiling
            - Interactive visualizations
            - Auto-fix capabilities
            - Exportable Python code
            - PDF reports
            
            Built with Streamlit, scikit-learn, and pandas.
            """)
        
        # Return settings dictionary
        # IMPORTANT: These keys must match what app.py and other files expect
        return {
            # Core settings (required by app.py and analysis.py)
            'ai_sensitivity': ai_sensitivity,           # Float: 0.02, 0.05, or 0.10
            'imputation_method': imputation_method,     # String: 'mice', 'mean', or 'drop'
            'show_3d_pca': show_3d_pca,                 # Boolean
            
            # Additional settings
            'sensitivity_label': sensitivity,           # String: 'low', 'medium', 'high'
            'include_code': include_code,
            'include_visualizations': include_visualizations,
            'max_categories': max_categories,
            'correlation_threshold': correlation_threshold,
            'pca_components': pca_components
        }