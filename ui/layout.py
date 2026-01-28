"""
UI Layout Components
Page configuration and hero section
"""
import streamlit as st


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Smart CSV Health Checker AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def render_hero_section():
    """Render the hero section with animated title and tagline"""
    st.markdown('''
    <div class="hero-container">
        <div class="hero-icon">🧠</div>
        <h1 class="hero-title">Smart CSV Health Checker</h1>
        <p class="hero-subtitle">AI-Powered Data Quality Analysis • Diagnose • Visualize • Repair</p>
        <div class="ai-badge">⚡ Powered by Machine Learning</div>
    </div>
    ''', unsafe_allow_html=True)