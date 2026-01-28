"""
Tab 5: Visualizations
Charts for categorical, numeric, datetime, and correlations
"""
import streamlit as st
import pandas as pd
import plotly.express as px


def render_visualizations_tab(df, col_types, results):
    """Render the Visualizations tab"""
    
    st.markdown('<h2 class="gradient-header">📊 Data Visualizations</h2>', unsafe_allow_html=True)
    
    # Categorical Data
    if col_types['categorical']:
        st.markdown("#### 📤 Categorical Data Insights")
        cat_col = st.selectbox("Select Categorical Column", col_types['categorical'])
        
        if cat_col:
            c1, c2 = st.columns([2, 1])
            
            with c1:
                top_n = df[cat_col].value_counts().head(10)
                fig_cat = px.bar(
                    top_n, x=top_n.index, y=top_n.values,
                    title=f"Top 10 Categories in '{cat_col}'",
                    color_discrete_sequence=['#8b5cf6'],
                    labels={'y': 'Count', 'index': cat_col}
                )
                fig_cat.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0')
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with c2:
                st.metric("Unique Values (Cardinality)", df[cat_col].nunique())
                st.markdown("**Distribution:**")
                dist_df = df[cat_col].value_counts(normalize=True).head(10).mul(100).round(1).astype(str) + '%'
                st.dataframe(dist_df)
        
        st.markdown("---")
    
    # Numeric Distribution
    if col_types['numeric']:
        st.markdown("#### 🔢 Numeric Distribution")
        sel_num = st.selectbox("Select Numeric Column", col_types['numeric'])
        
        mean_val = df[sel_num].mean()
        std_val = df[sel_num].std()
        
        c1, c2 = st.columns(2)
        
        with c1:
            fig = px.histogram(
                df, x=sel_num,
                title=f"Distribution of {sel_num} (μ={mean_val:.2f}, σ={std_val:.2f})",
                color_discrete_sequence=['#6366f1'],
                nbins=30
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            fig = px.box(
                df, y=sel_num,
                title=f"Outliers in {sel_num}",
                color_discrete_sequence=['#8b5cf6']
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Time Series
    if col_types['datetime']:
        st.markdown("---")
        sel_date = st.selectbox("Select Date Column", col_types['datetime'])
        
        try:
            ts_df = df.groupby(sel_date).size().reset_index(name='Count')
            fig = px.line(
                ts_df, x=sel_date, y='Count',
                title=f"Time Series - {sel_date}",
                color_discrete_sequence=['#10b981']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate time series: {e}")
    
    # Correlation Heatmap
    if len(col_types['numeric']) > 1:
        st.markdown("---")
        st.markdown('<h2 class="gradient-header">🔥 Correlation Heatmap</h2>', unsafe_allow_html=True)
        
        corr = df[col_types['numeric']].corr()
        fig_corr = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale='RdBu_r', zmin=-1, zmax=1,
            title="Feature Correlation Matrix",
            labels=dict(color="Correlation")
        )
        fig_corr.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=600
        )
        st.plotly_chart(fig_corr, use_container_width=True)