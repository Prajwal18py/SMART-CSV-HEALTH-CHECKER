"""
Tab 1: Overview
Main dashboard with issues, recommendations, and column profiling
"""
import streamlit as st
import plotly.express as px
from export.pdf_generator import generate_executive_scorecard, REPORTLAB_AVAILABLE
import pandas as pd

# ══════════════════════════════════════════════════════════════════════
# ENHANCED CSS - MATCHING EDA STYLE
# ══════════════════════════════════════════════════════════════════════
OVERVIEW_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* Alert cards matching EDA */
.eda-alert {
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin-bottom: .7rem;
    display: flex;
    align-items: flex-start;
    gap: .9rem;
    border: 1px solid;
    transition: transform .2s, box-shadow .2s;
}
.eda-alert:hover { 
    transform: translateX(4px); 
    box-shadow: 0 4px 16px rgba(99,102,241,.15);
}
.eda-alert.critical {
    background: rgba(239,68,68,.08);
    border-color: rgba(239,68,68,.35);
}
.eda-alert.warning {
    background: rgba(251,191,36,.07);
    border-color: rgba(251,191,36,.3);
}
.eda-alert.info {
    background: rgba(99,102,241,.07);
    border-color: rgba(99,102,241,.25);
}
.eda-alert.success {
    background: rgba(16,185,129,.07);
    border-color: rgba(16,185,129,.25);
}
.alert-icon { font-size: 1.3rem; line-height: 1; flex-shrink:0; padding-top:.1rem; }
.alert-title { color:#e2e8f0; font-weight:600; font-size:.88rem; margin:0 0 .15rem 0; }
.alert-body { color:rgba(203,213,224,.65); font-size:.78rem; margin:0; line-height:1.5; }

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

/* Profile cards */
.profile-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 14px;
    padding: 1rem;
    transition: border-color .25s, box-shadow .25s, transform .25s;
}
.profile-card:hover {
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

def render_overview_tab(df, results, col_types):
    """Render the Overview tab with enhanced UI matching EDA style"""
    
    # Apply enhanced CSS
    st.markdown(OVERVIEW_CSS, unsafe_allow_html=True)
    
    col_L, col_R = st.columns(2)
    
    # =================================================================
    # LEFT COLUMN: ISSUES WITH EDA STYLING
    # =================================================================
    with col_L:
        st.markdown("""
        <div class="eda-section-head">
            <span class="icon">🚨</span>
            <p class="title">Issues Detected</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not results['issues']:
            st.markdown("""
            <div class="eda-alert success">
                <span class="alert-icon">✅</span>
                <div>
                    <p class="alert-title">No Issues Found!</p>
                    <p class="alert-body">Your data appears to be clean and well-structured.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for issue in results['issues']:
                icon = "🤖" if "AI" in issue['type'] else "🚨" if issue['severity'] == 'High' else "⚠️"
                
                if issue['severity'] == 'High':
                    level = "critical"
                elif issue['severity'] == 'Medium':
                    level = "warning"
                else:
                    level = "info"
                
                st.markdown(f"""
                <div class="eda-alert {level}">
                    <span class="alert-icon">{icon}</span>
                    <div>
                        <p class="alert-title">{issue['type']}</p>
                        <p class="alert-body">{issue['message']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # =================================================================
    # RIGHT COLUMN: RECOMMENDATIONS WITH EDA STYLING
    # =================================================================
    with col_R:
        st.markdown("""
        <div class="eda-section-head">
            <span class="icon">💡</span>
            <p class="title">Recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not results['recommendations']:
            st.markdown("""
            <div class="eda-alert success">
                <span class="alert-icon">✨</span>
                <div>
                    <p class="alert-title">No Action Needed!</p>
                    <p class="alert-body">Your data is in excellent condition.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for rec in results['recommendations']:
                st.markdown(f"""
                <div class="eda-alert info">
                    <span class="alert-icon">💡</span>
                    <div>
                        <p class="alert-body">{rec}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
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
                "application/pdf"
            )
    else:
        st.warning("⚠️ Install 'reportlab' to enable PDF Scorecards")
    
    # =================================================================
    # COMPLETE COLUMN-BY-COLUMN PROFILER WITH EDA STYLING
    # =================================================================
    if st.button("📊 Generate Complete Data Profile", type="primary"):
        st.markdown("""
        <div class="eda-section-head">
            <span class="icon">📊</span>
            <p class="title">Complete Column-by-Column Profile</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                        st.plotly_chart(fig)
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
                        st.plotly_chart(fig)
                
                # Quality indicator with card styling
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
                <div class="profile-card" style="text-align: center; margin-top: 1rem;">
                    <div style="color: {quality_color}; font-weight: 700; font-family: 'Syne', sans-serif;">
                        Column Quality: {quality_score}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)