"""
Tab: PCA Analysis
Advanced PCA with 2D/3D visualization, biplot, scree plot, and smart data integration
NOW WITH: Enhanced UI matching EDA tab design
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from utils.export_utils import smart_download_button, get_format_label

# ══════════════════════════════════════════════════════════════════════
# ENHANCED CSS - MATCHING EDA TAB
# ══════════════════════════════════════════════════════════════════════
PCA_CSS = """
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
.eda-section-head .count {
    margin-left: auto;
    background: rgba(99,102,241,.2);
    color: #a5b4fc;
    border-radius: 20px;
    padding: .15rem .6rem;
    font-size: .72rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

/* Status cards */
.status-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.3);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.status-card:hover {
    border-color: rgba(99,102,241,.6);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,.2);
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(30,41,59,.8), rgba(15,23,42,.8));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 12px;
    padding: .9rem;
    text-align: center;
    height: 100%;
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(99,102,241,.2);
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

def render_pca_tab(df, results, col_types, settings=None):
    """Render the enhanced PCA tab with EDA styling"""
    
    # Apply enhanced CSS
    st.markdown(PCA_CSS, unsafe_allow_html=True)
    
    st.subheader("📉 Principal Component Analysis")
    
    # Smart data source selection
    pca_df = _get_best_data_source(df)
    data_source = _get_data_source_name()
    
    if data_source != "Original":
        st.success(f"✅ Using **{data_source}** data for PCA (recommended!)", icon="🎯")
    
    numeric_cols = pca_df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("❌ PCA requires at least 2 numeric columns!")
        st.info("💡 Visit **Feature Engineering** tab to create more numeric features.")
        return
    
    valid_numeric_cols = [
        col for col in numeric_cols
        if pca_df[col].nunique() > 1 and not pca_df[col].isna().all()
    ]
    
    if len(valid_numeric_cols) < 2:
        st.error("❌ Not enough valid numeric columns (need at least 2 with varying values)")
        return
    
    X = pca_df[valid_numeric_cols].fillna(pca_df[valid_numeric_cols].mean())
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca_full = PCA()
    pca_full.fit(X_scaled)
    
    explained_variance = pca_full.explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance)
    
    # ========================================================
    # SECTION 1: OVERVIEW METRICS WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">📊</span>
        <p class="title">PCA Overview</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Original Features", len(valid_numeric_cols))
    
    with col2:
        n_90 = np.argmax(cumulative_variance >= 0.9) + 1 if (cumulative_variance >= 0.9).any() else len(explained_variance)
        st.metric("For 90% Variance", n_90,
                 delta=f"-{len(valid_numeric_cols)-n_90}",
                 help="Components needed to retain 90% of variance")
    
    with col3:
        n_95 = np.argmax(cumulative_variance >= 0.95) + 1 if (cumulative_variance >= 0.95).any() else len(explained_variance)
        st.metric("For 95% Variance", n_95,
                 delta=f"-{len(valid_numeric_cols)-n_95}",
                 help="Components needed to retain 95% of variance")
    
    with col4:
        reduction_pct = ((len(valid_numeric_cols) - n_90) / len(valid_numeric_cols)) * 100
        st.metric("Potential Reduction", f"{reduction_pct:.0f}%",
                 help="Feature reduction at 90% variance threshold")
    
    st.markdown("---")
    
    # ========================================================
    # SECTION 2: VISUALIZATIONS
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">📈</span>
        <p class="title">Variance Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
        "📊 Scree Plot",
        "📈 Cumulative Variance",
        "🎯 2D Projection",
        "🔮 3D Projection"
    ])
    
    # TAB 1: SCREE PLOT
    with viz_tab1:
        st.caption("Find the 'elbow' - point where adding components doesn't help much")
        
        fig_scree = go.Figure()
        fig_scree.add_trace(go.Scatter(
            x=list(range(1, len(explained_variance) + 1)),
            y=explained_variance,
            mode='lines+markers',
            name='Explained Variance',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=10, color='#6366f1'),
            hovertemplate='PC%{x}<br>Variance: %{y:.3f}<extra></extra>'
        ))
        
        if n_90 <= len(explained_variance):
            fig_scree.add_vline(
                x=n_90,
                line_dash="dash",
                line_color="#10b981",
                annotation_text=f"90% threshold (PC{n_90})",
                annotation_position="top"
            )
        
        fig_scree.update_layout(
            title="Scree Plot - Explained Variance by Component",
            xaxis_title="Principal Component",
            yaxis_title="Explained Variance Ratio",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_scree)
        
        with st.expander("📋 Detailed Variance Table"):
            variance_df = pd.DataFrame({
                'Component': [f'PC{i+1}' for i in range(len(explained_variance))],
                'Variance %': explained_variance * 100,
                'Cumulative %': cumulative_variance * 100
            })
            st.dataframe(
                variance_df.style.format({
                    'Variance %': '{:.2f}%',
                    'Cumulative %': '{:.2f}%'
                }).background_gradient(subset=['Variance %'], cmap='Blues'),
                height=300
            )
    
    # TAB 2: CUMULATIVE VARIANCE
    with viz_tab2:
        st.caption("See how many components you need for desired variance retention")
        
        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Bar(
            x=list(range(1, len(explained_variance) + 1)),
            y=explained_variance,
            name='Individual',
            marker_color='#6366f1',
            opacity=0.6,
            hovertemplate='PC%{x}<br>Individual: %{y:.3f}<extra></extra>'
        ))
        fig_cumulative.add_trace(go.Scatter(
            x=list(range(1, len(cumulative_variance) + 1)),
            y=cumulative_variance,
            name='Cumulative',
            line=dict(color='#10b981', width=3),
            mode='lines+markers',
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='PC%{x}<br>Cumulative: %{y:.1%}<extra></extra>'
        ))
        
        fig_cumulative.add_shape(
            type="line", x0=0, x1=len(cumulative_variance), y0=0.90, y1=0.90,
            line=dict(dash="dash", color="#10b981", width=2), yref='y2'
        )
        fig_cumulative.add_annotation(
            x=len(cumulative_variance) * 0.95, y=0.90, text="90%",
            showarrow=False, yref='y2', font=dict(color="#10b981")
        )
        fig_cumulative.add_shape(
            type="line", x0=0, x1=len(cumulative_variance), y0=0.95, y1=0.95,
            line=dict(dash="dash", color="#fbbf24", width=2), yref='y2'
        )
        fig_cumulative.add_annotation(
            x=len(cumulative_variance) * 0.95, y=0.95, text="95%",
            showarrow=False, yref='y2', font=dict(color="#fbbf24")
        )
        
        fig_cumulative.update_layout(
            title="Explained Variance - Individual and Cumulative",
            xaxis_title="Principal Component",
            yaxis=dict(title="Individual Variance", side='left'),
            yaxis2=dict(title="Cumulative Variance", overlaying='y', side='right', tickformat='.0%'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_cumulative)
    
    # TAB 3: 2D PROJECTION
    with viz_tab3:
        st.caption("Visualize data in 2D principal component space")
        
        pca_2d = PCA(n_components=2)
        components_2d = pca_2d.fit_transform(X_scaled)
        
        plot_df = pd.DataFrame({
            'PC1': components_2d[:, 0],
            'PC2': components_2d[:, 1],
            'Index': range(len(components_2d))
        })
        
        cat_cols = pca_df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if cat_cols:
            color_col = st.selectbox("Color points by:", ['None'] + cat_cols, key='pca_2d_color')
            if color_col != 'None':
                plot_df['Category'] = pca_df[color_col].astype(str)
                fig_2d = px.scatter(plot_df, x='PC1', y='PC2', color='Category',
                                    title=f"2D PCA Projection (colored by {color_col})",
                                    hover_data={'Index': True})
            else:
                fig_2d = px.scatter(plot_df, x='PC1', y='PC2',
                                    title="2D PCA Projection", hover_data={'Index': True})
        else:
            fig_2d = px.scatter(plot_df, x='PC1', y='PC2',
                                title="2D PCA Projection", hover_data={'Index': True})
        
        fig_2d.update_traces(marker=dict(size=8, opacity=0.7))
        fig_2d.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=500,
            xaxis_title=f"PC1 ({pca_2d.explained_variance_ratio_[0]:.1%} variance)",
            yaxis_title=f"PC2 ({pca_2d.explained_variance_ratio_[1]:.1%} variance)"
        )
        st.plotly_chart(fig_2d)
        
        if st.checkbox("Show feature loadings (biplot)", key='show_biplot'):
            loadings_2d = pca_2d.components_.T * np.sqrt(pca_2d.explained_variance_)
            fig_biplot = go.Figure()
            fig_biplot.add_trace(go.Scatter(
                x=components_2d[:, 0], y=components_2d[:, 1],
                mode='markers',
                marker=dict(size=6, color='#6366f1', opacity=0.5),
                name='Data Points',
                hovertemplate='PC1: %{x:.2f}<br>PC2: %{y:.2f}<extra></extra>'
            ))
            
            loading_importance = np.sqrt(loadings_2d[:, 0]**2 + loadings_2d[:, 1]**2)
            top_features = np.argsort(loading_importance)[-10:]
            
            for idx in top_features:
                fig_biplot.add_annotation(
                    ax=0, ay=0,
                    x=loadings_2d[idx, 0] * 3, y=loadings_2d[idx, 1] * 3,
                    xref='x', yref='y', axref='x', ayref='y',
                    showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
                    arrowcolor='#10b981',
                    text=valid_numeric_cols[idx],
                    font=dict(size=10, color='#10b981')
                )
            
            fig_biplot.update_layout(
                title="PCA Biplot - Top 10 Feature Loadings",
                xaxis_title=f"PC1 ({pca_2d.explained_variance_ratio_[0]:.1%})",
                yaxis_title=f"PC2 ({pca_2d.explained_variance_ratio_[1]:.1%})",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=500
            )
            st.plotly_chart(fig_biplot)
    
    # TAB 4: 3D PROJECTION
    with viz_tab4:
        if len(valid_numeric_cols) >= 3:
            st.caption("Interactive 3D visualization of data in principal component space")
            
            pca_3d = PCA(n_components=3)
            components_3d = pca_3d.fit_transform(X_scaled)
            
            plot_df_3d = pd.DataFrame({
                'PC1': components_3d[:, 0],
                'PC2': components_3d[:, 1],
                'PC3': components_3d[:, 2],
                'Index': range(len(components_3d))
            })
            
            if cat_cols:
                color_col = st.selectbox("Color points by:", ['None'] + cat_cols, key='pca_3d_color')
                if color_col != 'None':
                    plot_df_3d['Category'] = pca_df[color_col].astype(str)
                    fig_3d = px.scatter_3d(plot_df_3d, x='PC1', y='PC2', z='PC3',
                                           color='Category',
                                           title=f"3D PCA Projection (colored by {color_col})",
                                           hover_data={'Index': True})
                else:
                    fig_3d = px.scatter_3d(plot_df_3d, x='PC1', y='PC2', z='PC3',
                                           title="3D PCA Projection", hover_data={'Index': True})
            else:
                fig_3d = px.scatter_3d(plot_df_3d, x='PC1', y='PC2', z='PC3',
                                       title="3D PCA Projection", hover_data={'Index': True})
            
            fig_3d.update_traces(marker=dict(size=5, opacity=0.7))
            fig_3d.update_layout(
                scene=dict(
                    xaxis_title=f"PC1 ({pca_3d.explained_variance_ratio_[0]:.1%})",
                    yaxis_title=f"PC2 ({pca_3d.explained_variance_ratio_[1]:.1%})",
                    zaxis_title=f"PC3 ({pca_3d.explained_variance_ratio_[2]:.1%})",
                    bgcolor='rgba(0,0,0,0)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=600
            )
            st.plotly_chart(fig_3d)
            
            total_var_3d = sum(pca_3d.explained_variance_ratio_)
            st.info(f"💡 These 3 components capture **{total_var_3d:.1%}** of total variance")
        else:
            st.warning("⚠️ Need at least 3 numeric features for 3D visualization")
    
    st.markdown("---")
    
    # ========================================================
    # SECTION 3: DIMENSIONALITY REDUCTION WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🔬</span>
        <p class="title">Dimensionality Reduction</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Reduce dataset dimensions while preserving variance")
    
    col_slider, col_info = st.columns([2, 1])
    
    with col_slider:
        default_n = settings.get('pca_components', 3) if settings else 3
        n_components = st.slider(
            "Select number of components to keep",
            min_value=2,
            max_value=len(valid_numeric_cols),
            value=min(default_n, n_90, len(valid_numeric_cols)),
            help="Reduce features while keeping most variance"
        )
        variance_kept = cumulative_variance[n_components-1] * 100
        st.info(f"📊 **{n_components} components** will preserve **{variance_kept:.1f}%** of variance")
    
    with col_info:
        reduction_pct = ((len(valid_numeric_cols) - n_components) / len(valid_numeric_cols)) * 100
        st.metric("Original Features", len(valid_numeric_cols))
        st.metric("Reduced Features", n_components, delta=f"-{reduction_pct:.0f}%")
    
    if st.button("⚡ Generate Reduced Dataset", type="primary"):
        pca_model = PCA(n_components=n_components)
        reduced_data = pca_model.fit_transform(X_scaled)
        
        reduced_df = pd.DataFrame(
            reduced_data,
            columns=[f'PC{i+1}' for i in range(n_components)]
        )
        
        # Add non-numeric columns back
        for col in pca_df.columns:
            if col not in valid_numeric_cols:
                reduced_df[col] = pca_df[col].values
        
        st.session_state['pca_reduced_df'] = reduced_df
        st.session_state['pca_model'] = pca_model
        st.session_state['pca_scaler'] = scaler
        
        st.toast(f"Reduced to {n_components} features!", icon="✅")
        st.success(f"✅ Reduced from {len(valid_numeric_cols)} to {n_components} features ({reduction_pct:.0f}% reduction)!")
        
        st.subheader("👁️ Preview of Reduced Dataset")
        st.dataframe(reduced_df.head(20), height=300)
        
        # Feature loadings
        loadings = pd.DataFrame(
            pca_model.components_.T,
            columns=[f'PC{i+1}' for i in range(n_components)],
            index=valid_numeric_cols
        )
        
        with st.expander("🔍 Feature Loadings (How original features map to components)", expanded=False):
            st.caption("Higher absolute values indicate stronger influence on that component")
            st.dataframe(
                loadings.style.background_gradient(cmap='RdBu_r', axis=None, vmin=-1, vmax=1)
                .format(precision=3),
                height=400
            )
            
            st.markdown("#### 🎯 Top 5 Features per Component")
            for i in range(min(3, n_components)):
                st.markdown(f"**PC{i+1}** ({pca_model.explained_variance_ratio_[i]:.1%} variance)")
                top_features = loadings[f'PC{i+1}'].abs().sort_values(ascending=False).head(5)
                for feat, val in top_features.items():
                    sign = "+" if loadings.loc[feat, f'PC{i+1}'] > 0 else "-"
                    st.write(f"  {sign} {feat}: {abs(val):.3f}")
                st.write("")
        
        st.markdown("### 📥 Download Options")
        fmt = get_format_label()
        
        down_col1, down_col2, down_col3 = st.columns(3)
        
        with down_col1:
            smart_download_button(
                df=reduced_df,
                label=f"📊 Download Reduced ({fmt})",
                suffix=f"pca_{n_components}components",
                key="dl_pca_reduced",
                button_width=None
            )
        
        with down_col2:
            code = _generate_pca_code(n_components, valid_numeric_cols)
            st.download_button(
                "💻 Download PCA Code",
                code,
                "pca_transformation.py",
                "text/plain"
            )
        
        with down_col3:
            st.download_button(
                "📋 Download Loadings (CSV)",
                loadings.to_csv().encode('utf-8'),
                "pca_loadings.csv",
                "text/csv"
            )
        
        with st.expander("💻 View Python Code", expanded=False):
            st.code(code, language='python')


# ========================================================
# HELPER FUNCTIONS (UNCHANGED)
# ========================================================

def _get_best_data_source(df):
    """Get the most processed data source available"""
    if 'engineered_df' in st.session_state and st.session_state.engineered_df is not None:
        return st.session_state.engineered_df
    elif 'skew_fixed_df' in st.session_state and st.session_state.skew_fixed_df is not None:
        return st.session_state.skew_fixed_df
    elif 'global_cleaned_df' in st.session_state and st.session_state.global_cleaned_df is not None:
        return st.session_state.global_cleaned_df
    else:
        return df


def _get_data_source_name():
    """Get name of the data source being used"""
    if 'engineered_df' in st.session_state and st.session_state.engineered_df is not None:
        return "Feature Engineered"
    elif 'skew_fixed_df' in st.session_state and st.session_state.skew_fixed_df is not None:
        return "Skewness Corrected"
    elif 'global_cleaned_df' in st.session_state and st.session_state.global_cleaned_df is not None:
        return "Cleaned"
    else:
        return "Original"


def _generate_pca_code(n_components, feature_names):
    """Generate Python code for PCA transformation"""
    
    code = f"""# PCA Dimensionality Reduction
# Auto-generated by DataForge Studio

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib

# Load data
df = pd.read_csv('your_data.csv')

# Select numeric features used in PCA
feature_columns = {feature_names}
X = df[feature_columns]

# Handle missing values
X = X.fillna(X.mean())

# Standardize features (CRITICAL for PCA)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply PCA
pca = PCA(n_components={n_components})
X_reduced = pca.fit_transform(X_scaled)

# Create reduced dataframe
df_reduced = pd.DataFrame(
    X_reduced,
    columns=[f'PC{{i+1}}' for i in range({n_components})]
)

# Add back non-numeric columns
for col in df.columns:
    if col not in feature_columns:
        df_reduced[col] = df[col].values

# Save results
df_reduced.to_csv('data_pca_reduced.csv', index=False)

# Save fitted transformers for production use
joblib.dump(scaler, 'pca_scaler.pkl')
joblib.dump(pca, 'pca_model.pkl')

print(f'Original features: {{len(feature_columns)}}')
print(f'Reduced features: {n_components}')
print(f'Variance retained: {{pca.explained_variance_ratio_.sum():.1%}}')

# ============================================================
# APPLY TO NEW DATA (Production Use)
# ============================================================
# scaler = joblib.load('pca_scaler.pkl')
# pca = joblib.load('pca_model.pkl')
#
# new_df = pd.read_csv('new_data.csv')
# X_new = new_df[feature_columns].fillna(new_df[feature_columns].mean())
# X_new_scaled = scaler.transform(X_new)
# X_new_reduced = pca.transform(X_new_scaled)
# print(f'New data transformed: {{X_new_reduced.shape}}')
"""
    return code