"""
Tab 7 : Code Export
Python code generation for cleaning and AI training
"""
import streamlit as st
from export.code_generator import generate_cleaning_code, generate_ai_training_code


def render_code_tab(col_types, settings):
    """Render the Code Export tab"""
    
    st.subheader("💻 Python Generated Code")
    
    # Cleaning Code
    st.markdown("#### 🧹 Cleaning Code")
    
    if 'cleaning_ops' in st.session_state:
        code = generate_cleaning_code(st.session_state['cleaning_ops'])
        st.code(code, language='python')
        st.download_button(
            "📥 Download Python Script",
            code,
            "clean_data.py",
            "text/plain",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Apply fixes in 'Fix Data' tab first to generate code")
    
    st.markdown("---")
    
    # AI Training Code
    st.markdown("#### 🧠 AI Model Training Code")
    st.caption("Use this code to replicate the anomaly detection model in your own environment.")
    
    ai_code = generate_ai_training_code(col_types['numeric'], settings['ai_sensitivity'])
    st.code(ai_code, language='python')
    st.download_button(
        "📥 Download Training Script",
        ai_code,
        "train_model.py",
        "text/plain",
        use_container_width=True
    )
