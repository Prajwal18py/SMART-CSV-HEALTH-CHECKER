"""
Tab 6: Feature Engineering 
Transform and prepare features for machine learning with scaling, encoding, and advanced transformations
NOW WITH: Enhanced UI, glassmorphism design, hover effects matching EDA tab
"""
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, 
    LabelEncoder, PowerTransformer, QuantileTransformer,
    Normalizer, PolynomialFeatures
)
from sklearn.compose import ColumnTransformer
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.export_utils import smart_download_button, get_format_label


# ══════════════════════════════════════════════════════════════════════
# ✨ ENHANCED CSS - MATCHING EDA TAB DESIGN
# ══════════════════════════════════════════════════════════════════════
FEATURE_ENG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* ── Section Header ── */
.fe-section-head {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin: 1.6rem 0 1rem 0;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
    border-radius: 12px;
    border: 1px solid rgba(99, 102, 241, 0.2);
}

.fe-section-head .icon { font-size: 1.3rem; }
.fe-section-head .title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #c7d2fe;
    margin: 0;
}

/* ── Status Cards ── */
.status-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.status-card:hover {
    border-color: rgba(99, 102, 241, 0.6);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
}

.status-card.success {
    border-color: rgba(16, 185, 129, 0.4);
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%);
}

.status-card.warning {
    border-color: rgba(251, 191, 36, 0.4);
    background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(251, 191, 36, 0.05) 100%);
}

.status-card.info {
    border-color: rgba(99, 102, 241, 0.4);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
}

/* ── Transform Cards ── */
.transform-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(99, 102, 241, 0.18);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.7rem;
    transition: all 0.3s ease;
}

.transform-card:hover {
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.12);
    transform: translateX(4px);
}

.transform-title {
    font-family: 'DM Mono', monospace;
    color: #a5b4fc;
    font-size: 0.88rem;
    font-weight: 500;
    margin: 0 0 0.4rem 0;
}

.transform-badge {
    display: inline-block;
    padding: 0.12rem 0.45rem;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-right: 0.3rem;
}

.badge-scaling { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }
.badge-encoding { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-advanced { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }

/* ── Metric Cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.2);
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #e2e8f0;
    margin: 0;
}

.metric-label {
    font-size: 0.75rem;
    color: rgba(203, 213, 224, 0.6);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* ── Alert Cards ── */
.alert-box {
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin: 0.7rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    border: 1px solid;
    transition: transform 0.2s;
}

.alert-box:hover { transform: translateX(4px); }

.alert-box.error {
    background: rgba(239, 68, 68, 0.08);
    border-color: rgba(239, 68, 68, 0.35);
}

.alert-box.warning {
    background: rgba(251, 191, 36, 0.07);
    border-color: rgba(251, 191, 36, 0.3);
}

.alert-box.info {
    background: rgba(99, 102, 241, 0.07);
    border-color: rgba(99, 102, 241, 0.25);
}

.alert-box.success {
    background: rgba(16, 185, 129, 0.07);
    border-color: rgba(16, 185, 129, 0.25);
}

/* ── Progress Indicator ── */
.progress-step {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 1.2rem;
    background: rgba(99, 102, 241, 0.08);
    border-radius: 10px;
    margin-bottom: 0.5rem;
    border-left: 3px solid rgba(99, 102, 241, 0.5);
    transition: all 0.2s ease;
}

.progress-step:hover {
    background: rgba(99, 102, 241, 0.12);
    border-left-color: rgba(99, 102, 241, 0.8);
}

.progress-step.completed {
    border-left-color: #6ee7b7;
    background: rgba(16, 185, 129, 0.08);
}

/* ── Animation for processing ── */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 10px rgba(99, 102, 241, 0.2); }
    50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
}

.processing {
    animation: pulse-glow 2s ease-in-out infinite;
}

/* ── Button Hover Effects ── */
.stButton > button {
    transition: all 0.3s ease !important;
    border-radius: 12px !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(99,102,241, 0.3) !important;
}

.stDownloadButton > button {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
}
</style>
"""


def render_feature_engineering_tab(df, col_types):
    """
    Render the Feature Engineering tab with enhanced UI
    
    Args:
        df: DataFrame to engineer
        col_types: Dictionary with 'numeric' and 'categorical' column lists
    """
    # Inject CSS
    st.markdown(FEATURE_ENG_CSS, unsafe_allow_html=True)
    
    fmt_label = get_format_label()
    st.subheader("🔧 Feature Engineering")
    st.caption("Transform and prepare features for machine learning with scaling, encoding, and advanced transformations")
    
    # ========================================================
    # DATA SOURCE SELECTOR WITH ENHANCED UI
    # ========================================================
    cleaned_data_available = False
    skew_fixed_available = False
    data_sources = {"📄 Original Data": df}
    
    if 'global_cleaned_df' in st.session_state and st.session_state.global_cleaned_df is not None:
        data_sources["✅ Cleaned Data (Fix Data tab)"] = st.session_state.global_cleaned_df
        cleaned_data_available = True
    
    if 'skew_fixed_df' in st.session_state and st.session_state.skew_fixed_df is not None:
        data_sources["📐 Skewness-Corrected Data (Skewness tab)"] = st.session_state.skew_fixed_df
        skew_fixed_available = True
    
    # Workflow guidance with enhanced styling
    if skew_fixed_available:
        st.markdown("""
        <div class="status-card success">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2rem;">🎯</span>
                <div>
                    <p style="color: #6ee7b7; font-weight: 600; margin: 0; font-size: 0.95rem;">Great! Skewness-corrected data detected</p>
                    <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">This is the ideal starting point for feature engineering!</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif cleaned_data_available:
        st.markdown("""
        <div class="status-card info">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2rem;">💡</span>
                <div>
                    <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 0.95rem;">Tip: You have cleaned data</p>
                    <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">
                        For best results, visit the <strong>Skewness tab</strong> first to normalize distributions, then return here!
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card warning">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2rem;">🔄</span>
                <div>
                    <p style="color: #fbbf24; font-weight: 600; margin: 0; font-size: 0.95rem;">Recommended Workflow</p>
                    <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">
                        Clean your data in <strong>Fix Data</strong> tab → Normalize distributions in <strong>Skewness</strong> tab → 
                        Then return here for feature engineering!
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show data source selector if multiple sources available
    if len(data_sources) > 1:
        col_selector, col_info = st.columns([2, 1])
        
        with col_selector:
            default_index = 2 if skew_fixed_available else (1 if cleaned_data_available else 0)
            selected_source = st.selectbox(
                "📊 Choose Data Source",
                options=list(data_sources.keys()),
                index=default_index,
                help="Use the most processed version for best results"
            )
        
        with col_info:
            source_df = data_sources[selected_source]
            missing_count = source_df.isna().sum().sum()
            if missing_count == 0:
                st.metric("Data Quality", "✅ Clean", delta="Ready", delta_color="off")
            else:
                st.metric("Missing Values", missing_count, delta="⚠️ Needs fixing", delta_color="inverse")
        
        working_df = data_sources[selected_source].copy()
        st.markdown("---")
    else:
        working_df = df.copy()
    
    # Update col_types based on working_df
    numeric_cols = working_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = working_df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if len(numeric_cols) == 0 and len(categorical_cols) == 0:
        st.error("❌ No columns available for feature engineering!")
        return
    
    # Initialize session state
    if 'feature_engineering_applied' not in st.session_state:
        st.session_state.feature_engineering_applied = False
    if 'engineered_df' not in st.session_state:
        st.session_state.engineered_df = None
    if 'engineering_operations' not in st.session_state:
        st.session_state.engineering_operations = {
            'scaling': None,
            'encoding': None,
            'additional': []
        }
    
    # ========================================================
    # DATA QUALITY VALIDATION WITH ENHANCED UI
    # ========================================================
    issues = _validate_data_quality(working_df, numeric_cols, categorical_cols)
    
    if issues:
        with st.expander("⚠️ Data Quality Warnings", expanded=True):
            for issue in issues:
                st.markdown(f"""
                <div class="alert-box warning">
                    <span style="font-size: 1.3rem;">⚠️</span>
                    <p style="color: rgba(203,213,224,0.85); margin: 0; font-size: 0.85rem;">{issue}</p>
                </div>
                """, unsafe_allow_html=True)
            st.info("💡 Visit **Fix Data** and **Skewness** tabs first for best results!")
    
    # ========================================================
    # QUICK SETUP FOR ML
    # ========================================================
    with st.expander("⚡ Quick Setup (Recommended)", expanded=False):
        st.info("🎯 Apply ML best practices automatically")
        
        col_quick1, col_quick2 = st.columns(2)
        
        with col_quick1:
            if st.button("🚀 Auto-Configure for ML", type="primary"):
                if numeric_cols:
                    st.session_state.engineering_operations['scaling'] = {
                        'method': 'Standard Scaler (μ=0, σ=1)',
                        'columns': numeric_cols
                    }
                
                cat_cols_suitable = [c for c in categorical_cols if working_df[c].nunique() <= 10]
                if cat_cols_suitable:
                    st.session_state.engineering_operations['encoding'] = {
                        'method': 'One-Hot Encoding (Create dummy variables)',
                        'columns': cat_cols_suitable
                    }
                elif categorical_cols:
                    st.session_state.engineering_operations['encoding'] = {
                        'method': 'Label Encoding (Convert to integers)',
                        'columns': categorical_cols
                    }
                
                st.success("✅ Standard ML configuration applied!")
                st.rerun()
        
        with col_quick2:
            st.markdown("**What it does:**")
            st.caption("• Standard scaling for numeric features")
            st.caption("• One-hot encoding for categories (<10 unique)")
            st.caption("• Label encoding for high-cardinality")
    
    st.markdown("---")
    
    # Section header with enhanced styling
    st.markdown("""
    <div class="fe-section-head">
        <span class="icon">🎯</span>
        <p class="title">Configure Feature Engineering</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Select transformations to prepare your data for machine learning")
    
    # ========================================================
    # SECTION 1: FEATURE SCALING
    # ========================================================
    with st.expander("📏 **1. Feature Scaling** (Choose One)", expanded=True):
        st.caption("Scale numeric features to a common range")
        
        if not numeric_cols:
            st.info("ℹ️ No numeric columns available for scaling")
        else:
            cols_to_scale = st.multiselect(
                "Select numeric columns to scale:",
                numeric_cols,
                default=numeric_cols,
                key="scaling_cols"
            )
            
            if cols_to_scale:
                scaling_method = st.radio(
                    "Choose scaling method:",
                    [
                        "Standard Scaler (μ=0, σ=1)",
                        "MinMax Scaler (0-1 range)",
                        "Robust Scaler (outlier-safe)",
                        "None (Skip scaling)"
                    ],
                    help="""
                    **Standard Scaler:** Centers data around mean=0, std=1. Best for normally distributed data.
                    **MinMax Scaler:** Scales to 0-1 range. Good when you need bounded values.
                    **Robust Scaler:** Uses median and IQR. Best when you have outliers.
                    """,
                    key="scaling_method"
                )
                
                if scaling_method == "Robust Scaler (outlier-safe)":
                    st.info("💡 This scaler is recommended when you have outliers!", icon="🎯")
                
                if scaling_method != "None (Skip scaling)":
                    with st.expander("👁️ Preview Scaling Effect", expanded=False):
                        preview_col = st.selectbox("Preview column:", cols_to_scale, key="scale_preview")
                        
                        if preview_col:
                            original_data = working_df[preview_col].dropna()
                            
                            if "Standard" in scaling_method:
                                scaler = StandardScaler()
                            elif "MinMax" in scaling_method:
                                scaler = MinMaxScaler()
                            else:
                                scaler = RobustScaler()
                            
                            scaled_data = scaler.fit_transform(original_data.values.reshape(-1, 1)).flatten()
                            
                            fig = make_subplots(rows=1, cols=2, subplot_titles=("Original", "Scaled"))
                            fig.add_trace(go.Histogram(x=original_data, name="Original", marker_color='#FF4B4B'), row=1, col=1)
                            fig.add_trace(go.Histogram(x=scaled_data, name="Scaled", marker_color='#00CC96'), row=1, col=2)
                            fig.update_layout(height=300, showlegend=False)
                            st.plotly_chart(fig)
                            
                            stat_col1, stat_col2 = st.columns(2)
                            with stat_col1:
                                st.markdown("**Original Stats**")
                                st.write(f"Mean: {original_data.mean():.3f}")
                                st.write(f"Std: {original_data.std():.3f}")
                                st.write(f"Min: {original_data.min():.3f}")
                                st.write(f"Max: {original_data.max():.3f}")
                            with stat_col2:
                                st.markdown("**Scaled Stats**")
                                st.write(f"Mean: {np.mean(scaled_data):.3f}")
                                st.write(f"Std: {np.std(scaled_data):.3f}")
                                st.write(f"Min: {np.min(scaled_data):.3f}")
                                st.write(f"Max: {np.max(scaled_data):.3f}")
                
                if scaling_method != "None (Skip scaling)":
                    st.session_state.engineering_operations['scaling'] = {
                        'method': scaling_method,
                        'columns': cols_to_scale
                    }
                else:
                    st.session_state.engineering_operations['scaling'] = None
    
    # ========================================================
    # SECTION 2: CATEGORICAL ENCODING
    # ========================================================
    with st.expander("🏷️ **2. Categorical Encoding** (Choose One)", expanded=True):
        st.caption("Convert categorical variables to numeric")
        
        if not categorical_cols:
            st.info("ℹ️ No categorical columns available for encoding")
        else:
            cols_to_encode = st.multiselect(
                "Select categorical columns to encode:",
                categorical_cols,
                default=categorical_cols,
                key="encoding_cols"
            )
            
            if cols_to_encode:
                encoding_method = st.radio(
                    "Choose encoding method:",
                    [
                        "One-Hot Encoding (Create dummy variables)",
                        "Label Encoding (Convert to integers)",
                        "None (Skip encoding)"
                    ],
                    help="""
                    **One-Hot Encoding:** Creates binary columns for each category. Best for nominal categories.
                    **Label Encoding:** Assigns integer to each category. Use for ordinal categories or tree-based models.
                    """,
                    key="encoding_method"
                )
                
                if encoding_method != "None (Skip encoding)":
                    with st.expander("👁️ Preview Encoding Effect", expanded=False):
                        preview_col = st.selectbox("Preview column:", cols_to_encode, key="encode_preview")
                        
                        if preview_col:
                            unique_vals = working_df[preview_col].dropna().unique()
                            n_unique = len(unique_vals)
                            st.write(f"**Unique values:** {n_unique}")
                            
                            if n_unique <= 10:
                                st.write(f"**Categories:** {', '.join(map(str, unique_vals))}")
                            else:
                                st.write(f"**Sample categories:** {', '.join(map(str, unique_vals[:10]))}... (+{n_unique-10} more)")
                            
                            if "One-Hot" in encoding_method:
                                st.info(f"ℹ️ Will create **{n_unique}** new binary columns for this feature")
                                if n_unique > 20:
                                    st.warning(f"⚠️ High cardinality ({n_unique} categories)! Consider Label Encoding instead.", icon="💡")
                            else:
                                st.info(f"ℹ️ Will map categories to integers 0-{n_unique-1}")
                
                if encoding_method != "None (Skip encoding)":
                    st.session_state.engineering_operations['encoding'] = {
                        'method': encoding_method,
                        'columns': cols_to_encode
                    }
                else:
                    st.session_state.engineering_operations['encoding'] = None
    
    # ========================================================
    # SECTION 3: ADDITIONAL TRANSFORMATIONS
    # ========================================================
    with st.expander("✨ **3. Additional Transformations** (Optional - Pick Any)", expanded=True):
        st.caption("Advanced feature transformations for better model performance")
        
        additional_transforms = []
        
        # Normalization
        col_norm1, col_norm2 = st.columns([3, 1])
        with col_norm1:
            apply_normalization = st.checkbox(
                "**Normalization (L1/L2)** - Scale each sample to unit norm",
                help="Useful for text classification and clustering. Scales each row independently.",
                key="apply_norm"
            )
        with col_norm2:
            if apply_normalization:
                norm_type = st.selectbox("Type", ["L2", "L1"], key="norm_type")
        
        if apply_normalization:
            norm_cols = st.multiselect("Select columns for normalization:", numeric_cols, key="norm_cols")
            if norm_cols:
                additional_transforms.append({'type': 'normalization', 'norm': norm_type, 'columns': norm_cols})
        
        st.markdown("---")
        
        # Power Transform
        col_power1, col_power2 = st.columns([3, 1])
        with col_power1:
            apply_power = st.checkbox(
                "**Power Transform** - Make data more Gaussian-like",
                help="Applies Yeo-Johnson or Box-Cox transformation to stabilize variance and minimize skewness.",
                key="apply_power"
            )
        with col_power2:
            if apply_power:
                power_method = st.selectbox("Method", ["Yeo-Johnson", "Box-Cox"], key="power_method")
        
        if apply_power:
            power_cols = st.multiselect("Select columns for power transform:", numeric_cols, key="power_cols")
            
            if power_cols and power_method == "Box-Cox":
                has_negative = False
                negative_cols = []
                for col in power_cols:
                    if (working_df[col] <= 0).any():
                        has_negative = True
                        negative_cols.append(col)
                if has_negative:
                    st.error(
                        f"❌ **Box-Cox requires strictly positive values!**\n\n"
                        f"Columns with zero/negative values: {', '.join(negative_cols)}\n\n"
                        f"💡 **Solution:** Use **Yeo-Johnson** instead (works with any values)",
                        icon="⚠️"
                    )
                else:
                    st.success("✅ All selected columns are positive - Box-Cox is safe to use!", icon="✅")
            
            if power_cols:
                additional_transforms.append({'type': 'power', 'method': power_method, 'columns': power_cols})
        
        st.markdown("---")
        
        # Quantile Transform
        apply_quantile = st.checkbox(
            "**Quantile Transform** - Map to uniform or normal distribution",
            help="Transforms features to follow a uniform or Gaussian distribution. Robust to outliers.",
            key="apply_quantile"
        )
        
        if apply_quantile:
            q_col1, q_col2 = st.columns(2)
            with q_col1:
                quantile_cols = st.multiselect("Select columns:", numeric_cols, key="quantile_cols")
            with q_col2:
                quantile_output = st.selectbox("Output distribution:", ["uniform", "normal"], key="quantile_output")
            if quantile_cols:
                additional_transforms.append({
                    'type': 'quantile', 'output_distribution': quantile_output, 'columns': quantile_cols
                })
        
        st.markdown("---")
        
        # Polynomial Features
        apply_polynomial = st.checkbox(
            "**Polynomial Features** - Create interaction terms",
            help="Generates polynomial and interaction features. Warning: Can create many features!",
            key="apply_poly"
        )
        
        if apply_polynomial:
            poly_col1, poly_col2 = st.columns(2)
            with poly_col1:
                polynomial_cols = st.multiselect("Select columns:", numeric_cols, key="poly_cols")
            with poly_col2:
                poly_degree = st.slider("Degree:", 2, 3, 2, help="Degree 2 creates quadratic features, degree 3 cubic")
            
            if polynomial_cols:
                from math import comb
                n_features = len(polynomial_cols)
                n_output_features = sum(comb(n_features + d - 1, d) for d in range(1, poly_degree + 1))
                
                if n_output_features > 100:
                    st.error(
                        f"⚠️ **Warning:** Will create **{n_output_features}** features from {n_features} columns!\n\n"
                        f"This may cause memory issues. Consider:\n"
                        f"• Reducing degree to 2\n• Selecting fewer columns\n• Using only most important features",
                        icon="🚨"
                    )
                elif n_output_features > 50:
                    st.warning(f"⚠️ Will create **{n_output_features}** features from {n_features} columns")
                else:
                    st.info(f"ℹ️ Will create **{n_output_features}** features from {n_features} columns")
                
                additional_transforms.append({'type': 'polynomial', 'degree': poly_degree, 'columns': polynomial_cols})
        
        st.session_state.engineering_operations['additional'] = additional_transforms
    
    # ========================================================
    # ACTION BUTTONS & EXECUTION WITH ENHANCED UI
    # ========================================================
    st.markdown("---")
    
    # Enhanced section header
    st.markdown("""
    <div class="fe-section-head">
        <span class="icon">🚀</span>
        <p class="title">Apply Transformations</p>
    </div>
    """, unsafe_allow_html=True)
    
    operations_count = 0
    if st.session_state.engineering_operations['scaling']:
        operations_count += 1
    if st.session_state.engineering_operations['encoding']:
        operations_count += 1
    operations_count += len(st.session_state.engineering_operations['additional'])
    
    if operations_count == 0:
        st.info("📝 No transformations selected. Configure options above to get started.")
    else:
        st.success(f"✅ **{operations_count}** transformation(s) ready to apply")
        
        with st.expander("📋 View Transformation Summary", expanded=True):
            if st.session_state.engineering_operations['scaling']:
                scaling = st.session_state.engineering_operations['scaling']
                st.markdown(f"""
                <div class="transform-card">
                    <p class="transform-title">
                        <span class="transform-badge badge-scaling">SCALING</span>
                        {scaling['method']}
                    </p>
                    <p style="color: rgba(203,213,224,0.6); font-size: 0.8rem; margin: 0;">
                        {len(scaling['columns'])} columns selected
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.session_state.engineering_operations['encoding']:
                encoding = st.session_state.engineering_operations['encoding']
                st.markdown(f"""
                <div class="transform-card">
                    <p class="transform-title">
                        <span class="transform-badge badge-encoding">ENCODING</span>
                        {encoding['method']}
                    </p>
                    <p style="color: rgba(203,213,224,0.6); font-size: 0.8rem; margin: 0;">
                        {len(encoding['columns'])} columns selected
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            for transform in st.session_state.engineering_operations['additional']:
                if transform['type'] == 'normalization':
                    label = f"{transform['norm']} Normalization"
                elif transform['type'] == 'power':
                    label = f"{transform['method']} Transform"
                elif transform['type'] == 'quantile':
                    label = f"Quantile Transform ({transform['output_distribution']})"
                elif transform['type'] == 'polynomial':
                    label = f"Polynomial Features (degree {transform['degree']})"
                
                st.markdown(f"""
                <div class="transform-card">
                    <p class="transform-title">
                        <span class="transform-badge badge-advanced">ADVANCED</span>
                        {label}
                    </p>
                    <p style="color: rgba(203,213,224,0.6); font-size: 0.8rem; margin: 0;">
                        {len(transform['columns'])} columns selected
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        col_apply, col_reset = st.columns([3, 1])
        with col_apply:
            if st.button("✨ Apply All Transformations", type="primary"):
                _apply_feature_engineering(working_df, st.session_state.engineering_operations)
        with col_reset:
            if st.button("🔄 Reset", help="Clear all selections"):
                st.session_state.engineering_operations = {'scaling': None, 'encoding': None, 'additional': []}
                st.session_state.feature_engineering_applied = False
                st.session_state.engineered_df = None
                st.rerun()
    
    # ========================================================
    # RESULTS DISPLAY WITH ENHANCED UI
    # ========================================================
    if st.session_state.feature_engineering_applied and st.session_state.engineered_df is not None:
        st.markdown("---")
        
        # Enhanced results header
        st.markdown("""
        <div class="fe-section-head">
            <span class="icon">✅</span>
            <p class="title">Transformation Results</p>
        </div>
        """, unsafe_allow_html=True)
        
        engineered_df = st.session_state.engineered_df
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Original Columns", len(working_df.columns))
        with metric_col2:
            new_cols = len(engineered_df.columns) - len(working_df.columns)
            st.metric("New Columns", len(engineered_df.columns), delta=f"+{new_cols}")
        with metric_col3:
            st.metric("Rows", len(engineered_df))
        with metric_col4:
            missing = engineered_df.isna().sum().sum()
            st.metric("Missing Values", missing)
        
        with st.expander("👁️ Preview Engineered Data", expanded=True):
            st.dataframe(engineered_df.head(50), height=400)
        
        st.markdown("### 📥 Export Engineered Data")
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            smart_download_button(
                engineered_df,
                label=f"📥 Download {fmt_label}",
                suffix="feature_engineered",
                key="dl_feat_eng",
                button_type="primary",
                button_width='stretch' 
            )
        
        with download_col2:
            code = _generate_feature_engineering_code(st.session_state.engineering_operations)
            st.download_button(
                "📥 Download Python Code",
                data=code,
                file_name="feature_engineering_code.py",
                mime="text/plain"
            )
        
        with st.expander("💻 View Generated Python Code", expanded=False):
            st.code(code, language='python')
        
        st.info(
            "💡 **Next Step:** For classification problems, visit the **Imbalanced Data Handler** tab to fix class imbalance, then proceed to **Model Builder**!",
            icon="⚖️"
        )


# ========================================================
# HELPER FUNCTIONS (LOGIC UNCHANGED - UI ONLY)
# ========================================================

def _validate_data_quality(df, numeric_cols, categorical_cols):
    """Validate data quality and return list of issue warning strings."""
    issues = []
    
    missing = df.isna().sum().sum()
    if missing > 0:
        issues.append(f"**{missing} missing values detected** - Consider cleaning in Fix Data tab first")
    
    high_skew_cols = []
    for col in numeric_cols:
        if df[col].notna().sum() > 0:
            skew = df[col].skew()
            if abs(skew) > 1.0:
                high_skew_cols.append(f"{col} ({skew:.2f})")
    if high_skew_cols:
        issues.append(
            f"**High skewness detected** in {len(high_skew_cols)} column(s): {', '.join(high_skew_cols[:3])}"
            f"{' ...' if len(high_skew_cols) > 3 else ''} - Visit Skewness tab to normalize"
        )
    
    high_card_cols = []
    for col in categorical_cols:
        n_unique = df[col].nunique()
        if n_unique > 20:
            high_card_cols.append(f"{col} ({n_unique} categories)")
    if high_card_cols:
        issues.append(
            f"**High cardinality detected** in {len(high_card_cols)} column(s): {', '.join(high_card_cols[:2])}"
            f"{' ...' if len(high_card_cols) > 2 else ''} - Consider Label Encoding instead of One-Hot"
        )
    
    outlier_cols = []
    for col in numeric_cols:
        if df[col].notna().sum() > 0:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:  # ✅ Skip constant columns
                continue
            outlier_count = len(df[((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR)))])
            outlier_pct = outlier_count / len(df) * 100
            if outlier_pct > 1.0:  
                outlier_cols.append(col)
    if outlier_cols:
        issues.append(
            f"**Outliers still present** in {len(outlier_cols)} column(s): {', '.join(outlier_cols[:3])}"
            f"{' ...' if len(outlier_cols) > 3 else ''} — "
            f"Already treated? Use **Robust Scaler** above to handle remaining outliers safely."
        )
    
    return issues


def _apply_feature_engineering(df, operations):
    """Apply all selected feature engineering operations."""
    
    with st.status("🔄 Applying transformations...", expanded=True) as status:
        result_df = df.copy()
        
        # 1. Scaling
        if operations['scaling']:
            st.write(f"📏 Applying {operations['scaling']['method']}...")
            cols   = operations['scaling']['columns']
            method = operations['scaling']['method']
            if "Standard" in method:
                scaler = StandardScaler()
            elif "MinMax" in method:
                scaler = MinMaxScaler()
            else:
                scaler = RobustScaler()
            result_df[cols] = scaler.fit_transform(result_df[cols])
            st.write(f"   ✅ Scaled {len(cols)} columns")
        
        # 2. Encoding
        if operations['encoding']:
            st.write(f"🏷️ Applying {operations['encoding']['method']}...")
            cols   = operations['encoding']['columns']
            method = operations['encoding']['method']
            if "One-Hot" in method:
                result_df = pd.get_dummies(result_df, columns=cols, prefix=cols, drop_first=False)
                new_cols = len(result_df.columns) - len(df.columns) + len(cols)
                st.write(f"   ✅ Created {new_cols} dummy variables")
            else:
                for col in cols:
                    le = LabelEncoder()
                    result_df[col] = le.fit_transform(result_df[col].astype(str))
                st.write(f"   ✅ Label encoded {len(cols)} columns")
        
        # 3. Additional transforms
        for transform in operations['additional']:
            if transform['type'] == 'normalization':
                st.write(f"📊 Applying {transform['norm']} Normalization...")
                cols = transform['columns']
                normalizer = Normalizer(norm=transform['norm'].lower())
                result_df[cols] = normalizer.fit_transform(result_df[cols])
                st.write(f"   ✅ Normalized {len(cols)} columns")
            
            elif transform['type'] == 'power':
                st.write(f"⚡ Applying {transform['method']} Transform...")
                cols   = list(transform['columns'])
                method = 'yeo-johnson' if 'Yeo' in transform['method'] else 'box-cox'
                try:
                    if method == 'box-cox':
                        for col in list(cols):
                            if (result_df[col] <= 0).any():
                                st.error(f"   ❌ Skipped '{col}' - Box-Cox requires positive values")
                                cols.remove(col)
                    if cols:
                        pt = PowerTransformer(method=method)
                        result_df[cols] = pt.fit_transform(result_df[cols])
                        st.write(f"   ✅ Transformed {len(cols)} columns")
                except Exception as e:
                    st.warning(f"   ⚠️ Power transform failed: {str(e)}")
            
            elif transform['type'] == 'quantile':
                st.write(f"📈 Applying Quantile Transform...")
                cols = transform['columns']
                qt = QuantileTransformer(output_distribution=transform['output_distribution'])
                result_df[cols] = qt.fit_transform(result_df[cols])
                st.write(f"   ✅ Transformed {len(cols)} columns")
            
            elif transform['type'] == 'polynomial':
                st.write(f"🔢 Creating Polynomial Features (degree {transform['degree']})...")
                cols = transform['columns']
                poly = PolynomialFeatures(degree=transform['degree'], include_bias=False)
                poly_features      = poly.fit_transform(result_df[cols])
                poly_feature_names = poly.get_feature_names_out(cols)
                result_df = result_df.drop(columns=cols)
                poly_df   = pd.DataFrame(poly_features, columns=poly_feature_names, index=result_df.index)
                result_df = pd.concat([result_df, poly_df], axis=1)
                st.write(f"   ✅ Created {len(poly_feature_names)} polynomial features")
        
        status.update(label="✅ All transformations applied!", state="complete", expanded=False)
    
    st.session_state.engineered_df = result_df
    st.session_state.feature_engineering_applied = True
    st.toast("✨ Feature engineering complete!", icon="✅")
    st.rerun()


def _generate_feature_engineering_code(operations):
    """Generate Python code for the applied transformations."""
    
    code_lines = [
        "# Feature Engineering Pipeline",
        "# Auto-generated code for production use",
        "# Compatible with scikit-learn pipelines",
        "",
        "import pandas as pd",
        "import numpy as np",
        "from sklearn.preprocessing import (",
        "    StandardScaler, MinMaxScaler, RobustScaler,",
        "    LabelEncoder, PowerTransformer, QuantileTransformer,",
        "    Normalizer, PolynomialFeatures",
        ")",
        "from sklearn.pipeline import Pipeline",
        "from sklearn.compose import ColumnTransformer",
        "",
        "# Load your data — change path/format as needed",
        "df = pd.read_csv('your_data.csv')",
        "",
        "# ==================== FEATURE ENGINEERING ====================",
        "",
    ]
    
    if operations['scaling']:
        method = operations['scaling']['method']
        cols   = operations['scaling']['columns']
        code_lines.append("# 1. FEATURE SCALING")
        if "Standard" in method:
            code_lines.append("# Mean=0, Std=1 normalization")
            code_lines.append("scaler = StandardScaler()")
        elif "MinMax" in method:
            code_lines.append("# Scale to [0, 1] range")
            code_lines.append("scaler = MinMaxScaler()")
        else:
            code_lines.append("# Uses median and IQR (robust to outliers)")
            code_lines.append("scaler = RobustScaler()")
        code_lines.append(f"columns_to_scale = {cols}")
        code_lines.append("df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])")
        code_lines.append("")
    
    if operations['encoding']:
        method = operations['encoding']['method']
        cols   = operations['encoding']['columns']
        code_lines.append("# 2. CATEGORICAL ENCODING")
        if "One-Hot" in method:
            code_lines.append("# Create binary dummy variables for each category")
            code_lines.append(f"columns_to_encode = {cols}")
            code_lines.append("df = pd.get_dummies(df, columns=columns_to_encode, drop_first=False)")
        else:
            code_lines.append("# Convert categories to integer labels")
            code_lines.append(f"columns_to_encode = {cols}")
            code_lines.append("label_encoders = {}")
            code_lines.append("for col in columns_to_encode:")
            code_lines.append("    le = LabelEncoder()")
            code_lines.append("    df[col] = le.fit_transform(df[col].astype(str))")
            code_lines.append("    label_encoders[col] = le  # Save for inverse transform if needed")
        code_lines.append("")
    
    for transform in operations['additional']:
        if transform['type'] == 'normalization':
            code_lines.append(f"# {transform['norm']} NORMALIZATION")
            code_lines.append(f"normalizer = Normalizer(norm='{transform['norm'].lower()}')")
            code_lines.append(f"columns_to_normalize = {transform['columns']}")
            code_lines.append("df[columns_to_normalize] = normalizer.fit_transform(df[columns_to_normalize])")
            code_lines.append("")
        elif transform['type'] == 'power':
            method = 'yeo-johnson' if 'Yeo' in transform['method'] else 'box-cox'
            code_lines.append(f"# {transform['method'].upper()} POWER TRANSFORM")
            if method == 'box-cox':
                code_lines.append("# ⚠️ Box-Cox requires strictly positive values!")
                code_lines.append("for col in columns_to_transform:")
                code_lines.append("    if (df[col] <= 0).any():")
                code_lines.append("        print(f'WARNING: {col} contains non-positive values!')")
            else:
                code_lines.append("# Works with any values (positive, negative, zero)")
            code_lines.append(f"pt = PowerTransformer(method='{method}')")
            code_lines.append(f"columns_to_transform = {transform['columns']}")
            code_lines.append("df[columns_to_transform] = pt.fit_transform(df[columns_to_transform])")
            code_lines.append("")
        elif transform['type'] == 'quantile':
            code_lines.append(f"# QUANTILE TRANSFORM (Output: {transform['output_distribution']})")
            code_lines.append(f"qt = QuantileTransformer(output_distribution='{transform['output_distribution']}')")
            code_lines.append(f"columns_to_transform = {transform['columns']}")
            code_lines.append("df[columns_to_transform] = qt.fit_transform(df[columns_to_transform])")
            code_lines.append("")
        elif transform['type'] == 'polynomial':
            code_lines.append(f"# POLYNOMIAL FEATURES (Degree: {transform['degree']})")
            code_lines.append(f"poly = PolynomialFeatures(degree={transform['degree']}, include_bias=False)")
            code_lines.append(f"columns_for_poly = {transform['columns']}")
            code_lines.append("poly_features = poly.fit_transform(df[columns_for_poly])")
            code_lines.append("poly_feature_names = poly.get_feature_names_out(columns_for_poly)")
            code_lines.append("df = df.drop(columns=columns_for_poly)")
            code_lines.append("poly_df = pd.DataFrame(poly_features, columns=poly_feature_names, index=df.index)")
            code_lines.append("df = pd.concat([df, poly_df], axis=1)")
            code_lines.append("")
    
    code_lines.extend([
        "# ==================== SAVE ====================",
        "df.to_csv('data_feature_engineered.csv', index=False)",
        "print(f'✅ Feature engineering complete! Shape: {df.shape}')",
        "",
        "# ==================== OPTIONAL: SKLEARN PIPELINE ====================",
        "# pipeline = Pipeline([",
        "#     ('scaler', StandardScaler()),",
        "#     ('model', YourModel())",
        "# ])",
        "# pipeline.fit(X_train, y_train)",
    ])
    
    return "\n".join(code_lines)