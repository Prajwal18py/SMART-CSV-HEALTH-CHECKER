"""
Tab 2: AI Deep Dive
AI anomaly analysis, PCA visualization, feature importance, and anomaly explanation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle
from features.statistics import explain_anomaly, get_anomaly_severity


def render_ai_deep_dive_tab(df, results, col_types, settings):
    """Render the AI Deep Dive tab"""
    
    st.markdown('<h2 class="gradient-header">🧠 AI Anomaly Analysis</h2>', unsafe_allow_html=True)
    
    # =================================================================
    # MODEL EXPORT BUTTON
    # =================================================================
    if results['model']:
        model_bytes = pickle.dumps(results['model'])
        st.download_button(
            label="⬇️ Download Trained AI Model (.pkl)",
            data=model_bytes,
            file_name="isolation_forest_model.pkl",
            mime="application/octet-stream",
            help="Use this model to predict anomalies in production"
        )
        
        with st.expander("📘 How to Use Downloaded Model"):
            st.markdown("**Load and use the model to detect anomalies in new data:**")
            st.code("""import pickle
import pandas as pd

# Load the trained model
with open('isolation_forest_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load new data to check
new_data = pd.read_csv('new_data.csv')

# Predict anomalies
predictions = model.predict(new_data)

# Filter anomalies (-1 = Anomaly, 1 = Normal)
anomalies = new_data[predictions == -1]
print(f"Found {len(anomalies)} anomalies out of {len(new_data)} rows")

# Get anomaly scores (lower = more anomalous)
scores = model.score_samples(new_data)
new_data['anomaly_score'] = scores

# Save results
anomalies.to_csv('detected_anomalies.csv', index=False)""", language='python')
            st.info("💡 **Tip:** Use the same numeric columns that were used during training!")
        
        st.write("")
    
    # =================================================================
    # PCA VISUALIZATION WITH ANOMALIES
    # =================================================================
    if results['stats']['pca'] and results['stats']['ai_anomalies']:
        pca_data = results['stats']['pca']
        ai_data = results['stats']['ai_anomalies']
        
        # Detection summary
        ai_only = len(results['stats']['ai_anomalies']['indices'])
        stat_only = len(results['stats']['outlier_info'])
        
        st.info(f"""📊 **Detection Summary:**
        - Total rows analyzed: {len(df):,}
        - AI Anomalies Found: {ai_only} (Complex patterns)
        - Statistical Outliers: {stat_only} (Simple value checks)
        """)
        
        col_viz, col_explain = st.columns([3, 1])
        
        # Left: PCA Visualization
        with col_viz:
            pca_components = pca_data['components']
            labels = pca_data['anomaly_labels']
            
            if settings['show_3d_pca'] and pca_components.shape[1] >= 3:
                # 3D Plot
                plot_df = pd.DataFrame({
                    'PC1': pca_components[:, 0],
                    'PC2': pca_components[:, 1],
                    'PC3': pca_components[:, 2],
                    'Type': ['Anomaly' if x == -1 else 'Normal' for x in labels]
                })
                fig = px.scatter_3d(plot_df, x='PC1', y='PC2', z='PC3', color='Type',
                                   color_discrete_map={'Normal': '#10b981', 'Anomaly': '#ef4444'},
                                   title="AI Anomaly Detection (3D)", opacity=0.7)
            else:
                # 2D Plot
                plot_df = pd.DataFrame({
                    'PC1': pca_components[:, 0],
                    'PC2': pca_components[:, 1],
                    'Type': ['Anomaly' if x == -1 else 'Normal' for x in labels]
                })
                fig = px.scatter(plot_df, x='PC1', y='PC2', color='Type',
                               color_discrete_map={'Normal': '#10b981', 'Anomaly': '#ef4444'},
                               title=f"AI Anomaly Detection (n={len(plot_df):,})", opacity=0.7)
                fig.update_traces(marker=dict(size=8), selector=dict(name='Anomaly'))
                fig.update_traces(marker=dict(size=5), selector=dict(name='Normal'))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Right: Anomaly Explanation
        with col_explain:
            st.subheader("🔍 Explain Anomaly")
            
            anomaly_indices = ai_data['indices']
            if len(anomaly_indices) > 0:
                selected_idx = st.number_input("Row Index", 0, len(anomaly_indices)-1, 0)
                real_idx = anomaly_indices[selected_idx]
                row = df.iloc[real_idx]
                
                if st.button("Explain Why"):
                    explanations = explain_anomaly(row, df, results['stats']['feature_importance'])
                    st.markdown(f"### 🎯 Why Row {real_idx} is Anomalous")
                    
                    if explanations:
                        for exp in explanations:
                            st.warning(f"""
                            **{exp['column']}**: Value = {exp['value']:.2f}
                            - Typical range: {exp['typical_range']}
                            - Deviation: {exp['z_score']:.2f} standard deviations
                            - Severity: {exp['severity']}
                            """)
                    else:
                        st.info("💡 No single feature stands out. This is a complex multi-dimensional anomaly.")
        
        # =================================================================
        # ANOMALY TABLE
        # =================================================================
        st.markdown("---")
        st.subheader(f"🔍 Anomaly Rows ({len(ai_data['indices'])} detected)")
        
        col_table, col_scores = st.columns([3, 1])
        
        with col_table:
            anomaly_df = df.iloc[ai_data['indices']].copy()
            anomaly_df.insert(0, 'Index', ai_data['indices'])
            anomaly_df.insert(1, 'AI_Score', [f"{s:.4f}" for s in ai_data['scores']])
            anomaly_df.insert(2, 'Severity', [get_anomaly_severity(s) for s in ai_data['scores']])
            st.dataframe(anomaly_df.head(20), height=400)
            
            if len(ai_data['indices']) > 20:
                st.caption(f"Showing top 20 by severity (total: {len(ai_data['indices'])})")
        
        with col_scores:
            st.markdown("**Score Distribution**")
            score_fig = go.Figure(data=[go.Histogram(x=ai_data['scores'], nbinsx=20, marker_color='#ef4444')])
            score_fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                showlegend=False,
                xaxis_title="Score",
                yaxis_title="Count"
            )
            st.plotly_chart(score_fig, use_container_width=True)
        
        # =================================================================
        # FEATURE IMPORTANCE
        # =================================================================
        if results['stats']['feature_importance'] is not None:
            st.markdown("---")
            st.subheader("🎯 Feature Importance")
            st.caption("Which columns drove anomaly detection?")
            
            feat_imp = results['stats']['feature_importance']
            top_feature = feat_imp.iloc[0]
            
            st.markdown(
                f"💡 **Key Insight:** The **{top_feature['Feature']}** column has the highest "
                f"importance ({top_feature['Importance']:.2%}) in detecting anomalies."
            )
            
            fig_imp = px.bar(feat_imp.head(10), x='Importance', y='Feature', orientation='h',
                            title="Top 10 Features", color='Importance', color_continuous_scale='Purples')
            fig_imp.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig_imp, use_container_width=True)
    
    else:
        st.info("ℹ️ AI analysis requires 2+ numeric columns and 10+ rows")
    
    # =================================================================
    # STATISTICAL ANALYSIS
    # =================================================================
    st.markdown("---")
    st.markdown('<h2 class="gradient-header">📊 Statistical Analysis</h2>', unsafe_allow_html=True)
    
    c_skew, c_out = st.columns(2)
    
    with c_skew:
        st.markdown("#### 📉 Skewness")
        if not results['stats']['skew_info'].empty:
            st.dataframe(results['stats']['skew_info'])
        else:
            st.success("✅ Normal distributions")
    
    with c_out:
        st.markdown("#### 📊 Outliers (IQR)")
        if not results['stats']['outlier_info'].empty:
            st.dataframe(
                results['stats']['outlier_info'],
                column_config={
                    "Percentage": st.column_config.ProgressColumn(
                        "Outlier %",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100
                    )
                }
            )
        else:
            st.success("✅ No outliers")
    
    if not results['stats']['high_corr'].empty:
        st.markdown("#### 🔗 High Correlations")
        st.dataframe(results['stats']['high_corr'])