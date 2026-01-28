"""
Tab 1: Overview
Main dashboard with issues, recommendations, and column profiling
"""
import streamlit as st
import plotly.express as px
from export.pdf_generator import generate_executive_scorecard, REPORTLAB_AVAILABLE


def render_overview_tab(df, results, col_types):
    """Render the Overview tab with issues and recommendations"""
    
    col_L, col_R = st.columns(2)
    
    # =================================================================
    # LEFT COLUMN: ISSUES
    # =================================================================
    with col_L:
        st.subheader("🚨 Issues Detected")
        
        if not results['issues']:
            st.success("✅ No issues found!")
        else:
            for issue in results['issues']:
                icon = "🤖" if "AI" in issue['type'] else "🚨" if issue['severity'] == 'High' else "⚠️"
                
                if issue['severity'] == 'High':
                    st.error(f"{icon} **{issue['type']}**: {issue['message']}")
                elif issue['severity'] == 'Medium':
                    st.warning(f"{icon} **{issue['type']}**: {issue['message']}")
                else:
                    st.info(f"{icon} **{issue['type']}**: {issue['message']}")
    
    # =================================================================
    # RIGHT COLUMN: RECOMMENDATIONS
    # =================================================================
    with col_R:
        st.subheader("💡 Recommendations")
        
        if not results['recommendations']:
            st.success("✨ No action needed!")
        else:
            for rec in results['recommendations']:
                st.info(rec)
    
    # =================================================================
    # EXECUTIVE SCORECARD DOWNLOAD
    # =================================================================
    st.markdown("---")
    
    if REPORTLAB_AVAILABLE:
        pdf_data = generate_executive_scorecard(df, results)
        if pdf_data:
            st.download_button(
                "📊 Download Executive Scorecard (PDF)",
                pdf_data,
                "executive_scorecard.pdf",
                "application/pdf",
                use_container_width=True
            )
    else:
        st.warning("⚠️ Install 'reportlab' to enable PDF Scorecards")
    
    # =================================================================
    # COMPLETE COLUMN-BY-COLUMN PROFILER
    # =================================================================
    if st.button("📊 Generate Complete Data Profile", type="primary", use_container_width=True):
        st.markdown('<h2 class="gradient-header">📊 Complete Column-by-Column Profile</h2>', unsafe_allow_html=True)
        
        for col in df.columns:
            with st.expander(f"📌 {col} ({df[col].dtype})", expanded=False):
                c1, c2, c3 = st.columns(3)
                
                # Column 1: Basic stats
                with c1:
                    st.metric("Unique Values", f"{df[col].nunique():,}")
                    st.metric("Missing", f"{df[col].isna().sum():,} ({df[col].isna().mean()*100:.1f}%)")
                    
                    if pd.api.types.is_numeric_dtype(df[col]):
                        st.metric("Mean", f"{df[col].mean():.2f}")
                    else:
                        most_common = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
                        st.metric("Most Common", str(most_common)[:15])
                
                # Column 2: Advanced stats
                with c2:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        st.metric("Median", f"{df[col].median():.2f}")
                        st.metric("Std Dev", f"{df[col].std():.2f}")
                        st.metric("Min → Max", f"{df[col].min():.1f} → {df[col].max():.1f}")
                    else:
                        st.metric("Cardinality", f"{df[col].nunique() / len(df) * 100:.1f}%")
                        memory = df[col].memory_usage(deep=True) / 1024
                        st.metric("Memory", f"{memory:.1f} KB")
                
                # Column 3: Mini visualization
                with c3:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        fig = px.histogram(df, x=col, height=200, nbins=20,
                                          color_discrete_sequence=['#6366f1'])
                        fig.update_layout(
                            margin=dict(l=0, r=0, t=20, b=0),
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e2e8f0', size=9),
                            title=dict(text="Distribution", font=dict(size=10))
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        top_5 = df[col].value_counts().head(5)
                        fig = px.bar(x=top_5.values, y=top_5.index, orientation='h',
                                    height=200, color_discrete_sequence=['#8b5cf6'])
                        fig.update_layout(
                            margin=dict(l=0, r=0, t=20, b=0),
                            showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e2e8f0', size=9),
                            title=dict(text="Top 5 Values", font=dict(size=10))
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Quality indicator
                quality_score = 100
                if df[col].isna().mean() > 0.1:
                    quality_score -= 30
                if pd.api.types.is_numeric_dtype(df[col]):
                    if abs(df[col].skew()) > 2:
                        quality_score -= 20
                else:
                    if df[col].nunique() / len(df) > 0.95:
                        quality_score -= 20
                
                quality_color = "#10b981" if quality_score >= 80 else "#f59e0b" if quality_score >= 60 else "#ef4444"
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.02); border-radius: 8px; margin-top: 1rem;">
                    <div style="color: {quality_color}; font-weight: 700;">Column Quality: {quality_score}/100</div>
                </div>
                """, unsafe_allow_html=True)


# Import pandas for type checking
import pandas as pd