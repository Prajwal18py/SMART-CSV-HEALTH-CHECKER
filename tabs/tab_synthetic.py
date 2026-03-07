"""
Tab 10: Synthetic Data Generator
Generate synthetic data that mimics the statistical properties of the original dataset
NOW WITH: Enhanced UI matching EDA tab design
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.export_utils import smart_download_button, get_format_label

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════
# ENHANCED CSS - MATCHING EDA TAB
# ══════════════════════════════════════════════════════════════════════
SYNTHETIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* Section headers */
.eda-section-head {
    display: flex;
    align-items: center;
    gap: .7rem;
    margin: 1.6rem 0 1rem 0;
    padding-bottom: .5rem;
    border-bottom: 1px solid rgba(99,102,241,.2);
}
.eda-section-head .icon { font-size:1.3rem; }
.eda-section-head .title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #c7d2fe;
    margin: 0;
}

/* Config cards */
.config-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.25);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.config-card:hover {
    border-color: rgba(99,102,241,.5);
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(99,102,241,.12);
}

/* Buttons */
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

/* Expanders */
.streamlit-expanderHeader {
    transition: all 0.3s ease !important;
    border-radius: 8px !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(99, 102, 241, 0.05) !important;
    border-color: rgba(99, 102, 241, 0.3) !important;
}
</style>
"""


def render_synthetic_tab(df, col_types):
    """Render the Synthetic Data Generator tab with enhanced UI"""
    
    # Apply enhanced CSS
    st.markdown(SYNTHETIC_CSS, unsafe_allow_html=True)
    
    st.markdown('<h2 class="gradient-header">🧬 Synthetic Data Generator</h2>', unsafe_allow_html=True)
    st.caption("Generate realistic synthetic data that preserves statistical properties of your original dataset.")
    
    # ========================================================
    # CONFIGURATION SECTION WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">⚙️</span>
        <p class="title">Generation Settings</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Configure Generation Parameters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            n_samples = st.number_input(
                "Number of Synthetic Rows",
                min_value=10,
                max_value=100000,
                value=min(len(df), 1000),
                step=100,
                help="How many synthetic rows to generate"
            )
        
        with col2:
            preserve_correlations = st.checkbox(
                "Preserve Correlations",
                value=True,
                help="Maintain relationships between numeric columns"
            )
        
        with col3:
            add_noise = st.slider(
                "Noise Level",
                0.0, 0.5, 0.1, 0.05,
                help="Add randomness to prevent exact replication"
            )
    
    # ========================================================
    # COLUMN SELECTION WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">📋</span>
        <p class="title">Select Columns to Generate</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_options = list(df.columns)
    selected_cols = st.multiselect(
        "Columns to include in synthetic data",
        col_options,
        default=col_options[:min(10, len(col_options))],
        help="Select which columns to generate synthetic data for"
    )
    
    if not selected_cols:
        st.warning("⚠️ Please select at least one column")
        return
    
    st.markdown("---")
    
    if st.button("🚀 Generate Synthetic Data", type="primary"):
        with st.spinner("🧬 Generating synthetic data..."):
            progress = st.progress(0, text="Initializing...")
            
            try:
                synthetic_df = generate_synthetic_data(
                    df[selected_cols],
                    n_samples,
                    preserve_correlations,
                    add_noise,
                    col_types,
                    progress
                )
                
                progress.progress(1.0, text="✅ Complete!")
                
                st.session_state['synthetic_df'] = synthetic_df
                st.session_state['synthetic_original_cols'] = selected_cols
                st.success(f"✅ Generated {len(synthetic_df):,} synthetic rows!")
                
            except Exception as e:
                st.error(f"❌ Error generating synthetic data: {str(e)}")
    
    # ========================================================
    # RESULTS SECTION WITH ENHANCED UI
    # ========================================================
    if 'synthetic_df' in st.session_state:
        synthetic_df = st.session_state['synthetic_df']
        original_cols = st.session_state.get('synthetic_original_cols', selected_cols)
        
        display_original_cols = [c for c in original_cols if c in df.columns]
        
        st.markdown("""
        <div class="eda-section-head">
            <span class="icon">📊</span>
            <p class="title">Original vs Synthetic Comparison</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_preview, tab_stats, tab_viz = st.tabs(["Preview", "Statistics", "Visualizations"])
        
        with tab_preview:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Data (Sample)**")
                st.dataframe(df[display_original_cols].head(10), height=300)
            with col2:
                st.markdown("**Synthetic Data (Sample)**")
                st.dataframe(synthetic_df.head(10), height=300)
        
        with tab_stats:
            render_stats_comparison(df[display_original_cols], synthetic_df)
        
        with tab_viz:
            render_distribution_comparison(df[display_original_cols], synthetic_df)
        
        st.markdown("---")
        st.markdown("""
        <div class="eda-section-head">
            <span class="icon">📥</span>
            <p class="title">Download Synthetic Data</p>
        </div>
        """, unsafe_allow_html=True)
        
        fmt = get_format_label()
        
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            smart_download_button(
                df=synthetic_df,
                label=f"⬇️ Download Synthetic ({fmt})",
                suffix=f"synthetic_{n_samples}rows",
                key="dl_synthetic_only",
                button_width=None
            )
        
        with col_dl2:
            combined_df = pd.concat([df[display_original_cols], synthetic_df], ignore_index=True)
            combined_df['_is_synthetic'] = [False] * len(df) + [True] * len(synthetic_df)
            
            smart_download_button(
                df=combined_df,
                label=f"⬇️ Download Combined ({fmt})",
                suffix=f"combined_{len(combined_df)}rows",
                key="dl_synthetic_combined",
                button_width=None
            )


def generate_synthetic_data(df, n_samples, preserve_corr, noise_level, col_types, progress):
    """Generate synthetic data based on original dataset statistics"""
    
    synthetic_data = {}
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    
    if preserve_corr and len(numeric_cols) > 1:
        progress.progress(0.1, text="Computing correlation structure...")
        
        numeric_df = df[numeric_cols].dropna()
        
        if len(numeric_df) > 10:
            try:
                corr_matrix = numeric_df.corr().values
                
                eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix)
                eigenvalues = np.maximum(eigenvalues, 1e-8)
                corr_matrix = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
                
                L = np.linalg.cholesky(corr_matrix)
                
                uncorrelated = np.random.standard_normal((n_samples, len(numeric_cols)))
                correlated = uncorrelated @ L.T
                
                for i, col in enumerate(numeric_cols):
                    original = numeric_df[col].values
                    mean, std = original.mean(), original.std()
                    synthetic_data[col] = correlated[:, i] * std + mean
                    
                    if noise_level > 0:
                        noise = np.random.normal(0, std * noise_level, n_samples)
                        synthetic_data[col] += noise
                        
            except np.linalg.LinAlgError:
                preserve_corr = False
    
    progress.progress(0.3, text="Generating column data...")
    
    total_cols = len(df.columns)
    for idx, col in enumerate(df.columns):
        progress.progress(0.3 + 0.6 * (idx / total_cols), text=f"Processing {col}...")
        
        if col in synthetic_data:
            continue
        
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            synthetic_data[col] = [np.nan] * n_samples
            continue
        
        if pd.api.types.is_numeric_dtype(df[col]):
            synthetic_data[col] = generate_numeric_column(col_data, n_samples, noise_level)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            synthetic_data[col] = generate_datetime_column(col_data, n_samples)
        else:
            synthetic_data[col] = generate_categorical_column(col_data, n_samples)
    
    return pd.DataFrame(synthetic_data)


def generate_numeric_column(data, n_samples, noise_level):
    """Generate synthetic numeric column"""
    
    if SCIPY_AVAILABLE:
        try:
            distributions = [stats.norm, stats.lognorm, stats.expon]
            best_dist = None
            best_sse = np.inf
            
            for dist in distributions:
                try:
                    params = dist.fit(data)
                    fitted = dist.rvs(*params, size=len(data))
                    sse = np.sum((np.sort(data) - np.sort(fitted))**2)
                    if sse < best_sse:
                        best_sse = sse
                        best_dist = (dist, params)
                except:
                    continue
            
            if best_dist:
                return best_dist[0].rvs(*best_dist[1], size=n_samples)
        except:
            pass
    
    synthetic = np.random.choice(data, size=n_samples, replace=True)
    if noise_level > 0:
        noise = np.random.normal(0, data.std() * noise_level, n_samples)
        synthetic = synthetic + noise
    
    return synthetic


def generate_datetime_column(data, n_samples):
    """Generate synthetic datetime column"""
    min_date = data.min()
    max_date = data.max()
    
    if pd.isna(min_date) or pd.isna(max_date):
        return [pd.NaT] * n_samples
    
    date_range = (max_date - min_date).total_seconds()
    random_seconds = np.random.uniform(0, date_range, n_samples)
    return [min_date + pd.Timedelta(seconds=s) for s in random_seconds]


def generate_categorical_column(data, n_samples):
    """Generate synthetic categorical column"""
    value_counts = data.value_counts(normalize=True)
    return np.random.choice(
        value_counts.index,
        size=n_samples,
        p=value_counts.values,
        replace=True
    )


def render_stats_comparison(original, synthetic):
    """Render statistical comparison"""
    
    comparison_data = []
    
    for col in original.columns:
        if col not in synthetic.columns:
            continue
        if pd.api.types.is_numeric_dtype(original[col]):
            comparison_data.append({
                'Column': col, 'Metric': 'Mean',
                'Original': f"{original[col].mean():.2f}",
                'Synthetic': f"{synthetic[col].mean():.2f}"
            })
            comparison_data.append({
                'Column': col, 'Metric': 'Std Dev',
                'Original': f"{original[col].std():.2f}",
                'Synthetic': f"{synthetic[col].std():.2f}"
            })
        else:
            comparison_data.append({
                'Column': col, 'Metric': 'Unique Values',
                'Original': str(original[col].nunique()),
                'Synthetic': str(synthetic[col].nunique())
            })
    
    if comparison_data:
        st.dataframe(pd.DataFrame(comparison_data))
    else:
        st.info("No columns to compare")


def render_distribution_comparison(original, synthetic):
    """Render distribution comparison"""
    
    numeric_cols = [c for c in original.columns
                    if pd.api.types.is_numeric_dtype(original[c]) and c in synthetic.columns]
    
    if numeric_cols:
        selected_col = st.selectbox("Select column to visualize:", numeric_cols, key="synth_viz_col")
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=original[selected_col], name='Original', opacity=0.7, marker_color='#6366f1'))
        fig.add_trace(go.Histogram(x=synthetic[selected_col], name='Synthetic', opacity=0.7, marker_color='#10b981'))
        
        fig.update_layout(
            barmode='overlay',
            title=f"Distribution Comparison: {selected_col}",
            xaxis_title=selected_col,
            yaxis_title="Count",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig)
    else:
        st.info("No numeric columns available for visualization")