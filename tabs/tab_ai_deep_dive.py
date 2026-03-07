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

# ══════════════════════════════════════════════════════════════════════
# ENHANCED CSS - MATCHING EDA STYLE
# ══════════════════════════════════════════════════════════════════════
AI_DEEP_DIVE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* Section headers matching EDA style */
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

/* Info cards with hover */
.info-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: border-color .25s, box-shadow .25s, transform .25s;
}
.info-card:hover {
    border-color: rgba(99,102,241,.5);
    box-shadow: 0 4px 20px rgba(99,102,241,.12);
    transform: translateY(-2px);
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

/* Download buttons */
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

def render_ai_deep_dive_tab(df, results, col_types, settings):
    """Render the AI Deep Dive tab with enhanced UI"""
    
    # Apply enhanced CSS
    st.markdown(AI_DEEP_DIVE_CSS, unsafe_allow_html=True)
    
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
        
        # Detection summary with enhanced card
        ai_only = len(results['stats']['ai_anomalies']['indices'])
        stat_only = len(results['stats']['outlier_info'])
        
        st.markdown(f"""
        <div class="info-card">
            <div style="font-family: 'Syne', sans-serif; color: #a5b4fc; font-size: 1rem; font-weight: 600; margin-bottom: 0.8rem;">
                📊 Detection Summary
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-family: 'DM Mono', monospace; color: #e2e8f0; font-size: 1.5rem; font-weight: 600;">{len(df):,}</div>
                    <div style="color: rgba(203,213,224,.5); font-size: 0.75rem;">Total Rows</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'DM Mono', monospace; color: #6ee7b7; font-size: 1.5rem; font-weight: 600;">{ai_only}</div>
                    <div style="color: rgba(203,213,224,.5); font-size: 0.75rem;">AI Anomalies</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'DM Mono', monospace; color: #fbbf24; font-size: 1.5rem; font-weight: 600;">{stat_only}</div>
                    <div style="color: rgba(203,213,224,.5); font-size: 0.75rem;">Statistical Outliers</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
            st.plotly_chart(fig)
        
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
        # ✨ NEW: REMOVE ANOMALIES BUTTON
        # =================================================================
        st.markdown("---")
        st.markdown(f"""
        <div class="eda-section-head">
            <span class="icon">🗑️</span>
            <p class="title">Remove Anomalies</p>
            <span class="count">{len(ai_data['indices'])} detected</span>
        </div>
        """, unsafe_allow_html=True)
        
        col_remove_text, col_remove_btn = st.columns([3, 1])
        
        with col_remove_text:
            st.markdown(
                f"**{len(ai_data['indices'])} AI-detected anomalies** found. "
                "These are complex multi-dimensional outliers that can bias ML models. "
                "Click the button to remove them from your dataset."
            )
        
        with col_remove_btn:
            if st.button("🗑️ Remove All Anomalies", type="primary", width='stretch'):
                from utils.export_utils import smart_download_button, get_format_label
                fmt_label = get_format_label()
                
                with st.status("🔧 Removing anomalies...", expanded=True) as status:
                    st.write(f"🗑️ Removing {len(ai_data['indices'])} rows...")
                    
                    df_cleaned = df.drop(index=ai_data['indices']).reset_index(drop=True)
                    
                    st.write(f"✅ Removed {len(ai_data['indices'])} anomalies")
                    st.write(f"📊 Dataset: {len(df):,} → {len(df_cleaned):,} rows")
                    
                    st.session_state['anomaly_cleaned_df'] = df_cleaned
                    
                    status.update(label="✅ Anomalies removed!", state="complete", expanded=False)
                
                st.success(
                    f"✅ **Removed {len(ai_data['indices'])} anomaly rows!** "
                    f"Dataset reduced from {len(df):,} to {len(df_cleaned):,} rows."
                )
                
                st.info(
                    "💡 **Next Step:** Visit the **🛠️ Fix Data** tab to handle missing values, "
                    "duplicates, and remaining outliers in your cleaned dataset.",
                    icon="➡️"
                )
                
                smart_download_button(
                    df_cleaned,
                    label=f"⬇️ Download Anomaly-Free {fmt_label}",
                    suffix="anomaly_removed",
                    key="dl_anomaly_free",
                    button_width='stretch'
                )
                
                st.rerun()
        
        if st.session_state.get('anomaly_cleaned_df') is not None:
            st.success(
                f"✅ **Anomalies already removed!** "
                f"Working with {len(st.session_state['anomaly_cleaned_df']):,} clean rows. "
                "Continue to **Fix Data** tab.",
                icon="🎯"
            )
        # =================================================================
        # ANOMALY TABLE WITH SECTION HEADER
        # =================================================================
        st.markdown("---")
        st.markdown(f"""
        <div class="eda-section-head">
            <span class="icon">🔍</span>
            <p class="title">Anomaly Rows</p>
            <span class="count">{len(ai_data['indices'])} detected</span>
        </div>
        """, unsafe_allow_html=True)
        
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
            st.plotly_chart(score_fig)
        
        # =================================================================
        # FEATURE IMPORTANCE WITH SECTION HEADER
        # =================================================================
        if results['stats']['feature_importance'] is not None:
            st.markdown("---")
            st.markdown("""
            <div class="eda-section-head">
                <span class="icon">🎯</span>
                <p class="title">Feature Importance</p>
            </div>
            """, unsafe_allow_html=True)
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
            st.plotly_chart(fig_imp)
    
    else:
        st.info("ℹ️ AI analysis requires 2+ numeric columns and 10+ rows")
    
    # =================================================================
    # STATISTICAL ANALYSIS WITH SECTION HEADER
    # =================================================================
    st.markdown("---")
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">📊</span>
        <p class="title">Statistical Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
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