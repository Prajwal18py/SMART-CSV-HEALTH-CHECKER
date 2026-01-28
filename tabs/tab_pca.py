"""
Tab 6: PCA Analysis
PCA variance analysis and dimensionality reduction
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def render_pca_tab(df, results, col_types):
    """Render the PCA tab"""
    
    st.subheader("📉 Principal Component Analysis")
    
    if results['stats']['pca']:
        pca_data = results['stats']['pca']
        
        # Variance plot
        fig = go.Figure([
            go.Bar(y=pca_data['explained'], name='Individual Variance', marker_color='#6366f1'),
            go.Scatter(
                y=pca_data['cumulative'], name='Cumulative Variance',
                line=dict(color='#10b981', width=3),
                mode='lines+markers',
                marker=dict(size=8)
            )
        ])
        fig.update_layout(
            title="Explained Variance by Component",
            xaxis_title="Principal Component",
            yaxis_title="Variance Ratio",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            showlegend=True,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics
        n_90 = np.argmax(pca_data['cumulative'] >= 0.9) + 1
        n_95 = np.argmax(pca_data['cumulative'] >= 0.95) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Components for 90% Variance", n_90)
        with col2:
            st.metric("Components for 95% Variance", n_95)
        with col3:
            st.metric("Total Components", len(pca_data['explained']))
        
        # Dimensionality Reduction
        st.markdown("---")
        st.markdown('<h2 class="gradient-header">🔬 Dimensionality Reduction</h2>', unsafe_allow_html=True)
        st.caption("Reduce dataset dimensions while preserving variance")
        
        max_components = len(pca_data['explained'])
        
        col_slider, col_info = st.columns([2, 1])
        
        with col_slider:
            if max_components > 2:
                n_components = st.slider(
                    "Select number of components to keep",
                    min_value=2,
                    max_value=max_components,
                    value=min(n_90, max_components),
                    help="Reduce features while keeping most variance"
                )
            else:
                st.info(f"ℹ️ Dataset has {max_components} numeric columns. Slider disabled (requires > 2).")
                n_components = max_components
            
            variance_kept = pca_data['cumulative'][n_components-1] * 100
            st.info(f"📊 **{n_components} components** will preserve **{variance_kept:.1f}%** of variance")
        
        with col_info:
            original_features = len(col_types['numeric'])
            reduction_pct = ((original_features - n_components) / original_features) * 100
            st.metric("Original Features", original_features)
            st.metric("Reduced Features", n_components, delta=f"-{reduction_pct:.0f}%")
        
        if st.button("⚡ Generate Reduced Dataset", type="primary", use_container_width=True):
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df[col_types['numeric']].fillna(df[col_types['numeric']].mean()))
            
            pca_model = PCA(n_components=n_components)
            reduced_data = pca_model.fit_transform(scaled_data)
            
            reduced_df = pd.DataFrame(
                reduced_data,
                columns=[f'PC{i+1}' for i in range(n_components)]
            )
            
            # Add non-numeric columns
            for col in col_types['categorical'] + col_types['datetime'] + col_types['ids']:
                if col in df.columns:
                    reduced_df[col] = df[col].values
            
            st.toast(f"Reduced to {n_components} features!", icon="✅")
            st.success(f"✅ Reduced from {original_features} to {n_components} features!")
            
            st.subheader("Preview of Reduced Dataset")
            st.dataframe(reduced_df.head(10), height=300)
            
            with st.expander("🔍 Feature Loadings (How original features map to components)"):
                loadings = pd.DataFrame(
                    pca_model.components_.T,
                    columns=[f'PC{i+1}' for i in range(n_components)],
                    index=col_types['numeric']
                )
                st.dataframe(loadings.style.background_gradient(cmap='RdBu_r', axis=None))
            
            st.download_button(
                "⬇️ Download Reduced CSV",
                reduced_df.to_csv(index=False).encode('utf-8'),
                f"reduced_dataset_{n_components}components.csv",
                "text/csv",
                use_container_width=True
            )
    else:
        st.info("ℹ️ PCA requires 2+ numeric columns")