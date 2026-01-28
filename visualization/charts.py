"""
Chart and Visualization Components
Reusable visualization functions for metrics and charts
"""
import streamlit as st
from config.constants import COLORS
from features.statistics import get_health_grade


def render_dataset_overview_cards(df):
    """Render dataset overview metric cards"""
    st.markdown('<h2 class="gradient-header">📊 Dataset Overview</h2>', unsafe_allow_html=True)
    
    o1, o2, o3, o4, o5 = st.columns(5)
    
    render_overview_card(
        o1, f"{len(df):,}", "Rows", "🔢", COLORS['primary']
    )
    render_overview_card(
        o2, len(df.columns), "Columns", "🗂️", COLORS['secondary']
    )
    render_overview_card(
        o3, f"{df.memory_usage().sum()/1024**2:.1f} MB", "Memory", "💾", COLORS['success']
    )
    render_overview_card(
        o4, f"{df.isna().sum().sum():,}", "Missing", "❌", COLORS['danger']
    )
    render_overview_card(
        o5, df.duplicated().sum(), "Duplicates", "♊", COLORS['warning']
    )


def render_overview_card(column, value, label, icon, color):
    """Render a single metric card with glassmorphism style"""
    column.markdown(f"""
    <div class="metric-card" style="padding: 1rem; --card-color: {color}; --card-color-light: {color};">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value" style="font-size: 1.5rem;">{value}</div>
        <div class="metric-label" style="font-size: 0.7rem;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_overview_metrics(df, results, col_types):
    """Render main health metrics after analysis"""
    m1, m2, m3, m4 = st.columns(4)
    
    score = results['health_score']
    
    # Determine color based on score
    if score >= 80:
        color = COLORS['success']
        color_light = "#34d399"
    elif score >= 60:
        color = COLORS['warning']
        color_light = "#fbbf24"
    else:
        color = COLORS['danger']
        color_light = "#f87171"
    
    ai_anoms = len(results['stats']['ai_anomalies']['indices']) if results['stats']['ai_anomalies'] else 0
    
    # Health Score Card
    with m1:
        st.markdown(
            f'<div class="metric-card" style="--card-color: {color}; --card-color-light: {color_light};">'
            f'<div class="metric-icon">💯</div>'
            f'<div class="metric-value">{score}</div>'
            f'<div class="metric-label">Health Score</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Issues Card
    with m2:
        issue_count = len(results["issues"])
        if issue_count > 10:
            issue_color = COLORS['danger']
        elif issue_count > 5:
            issue_color = COLORS['warning']
        else:
            issue_color = COLORS['success']
        
        st.markdown(
            f'<div class="metric-card" style="--card-color: {issue_color};">'
            f'<div class="metric-icon">⚠️</div>'
            f'<div class="metric-value">{issue_count}</div>'
            f'<div class="metric-label">Total Issues</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # AI Anomalies Card
    with m3:
        st.markdown(
            f'<div class="metric-card ai-glow" style="--card-color: {COLORS["primary"]}; --card-color-light: #818cf8; border: 1px solid rgba(99, 102, 241, 0.5);">'
            f'<div class="metric-icon">🤖</div>'
            f'<div class="metric-value">{ai_anoms}</div>'
            f'<div class="metric-label">AI Anomalies</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Numeric Columns Card
    with m4:
        st.markdown(
            f'<div class="metric-card" style="--card-color: {COLORS["secondary"]}; --card-color-light: #a78bfa;">'
            f'<div class="metric-icon">🔢</div>'
            f'<div class="metric-value">{len(col_types["numeric"])}</div>'
            f'<div class="metric-label">Numeric Cols</div>'
            f'</div>',
            unsafe_allow_html=True
        )