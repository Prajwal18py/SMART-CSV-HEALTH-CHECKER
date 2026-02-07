"""
Tab: Code Export
Python code generation for cleaning and AI training
"""
import streamlit as st
import json
from export.code_generator import generate_cleaning_code, generate_ai_training_code


def render_code_tab(col_types, settings):
    """Render the Code Export tab"""
    
    st.subheader("💻 Python Generated Code")
    
    # Cleaning Code
    st.markdown("#### 🧹 Cleaning Code")
    
    if 'cleaning_ops' in st.session_state:  # ✅ FIXED: Removed 'ig' typo
        code = generate_cleaning_code(st.session_state['cleaning_ops'])
        st.code(code, language='python')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Cleaning Script",
                code,
                "clean_data.py",
                "text/plain",
                width="stretch"
            )
    else:
        st.warning("⚠️ Apply fixes in 'Fix Data' tab first to generate code")
    
    st.markdown("---")
    
    # ✅ NEW: Skewness Transformation Code
    st.markdown("#### 📐 Skewness Transformation Code")
    
    if 'transformations_log' in st.session_state and len(st.session_state['transformations_log']) > 0:
        skew_code = generate_skewness_code(st.session_state['transformations_log'])
        st.code(skew_code, language='python')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Skewness Script",
                skew_code,
                "transform_skewness.py",
                "text/plain",
                width="stretch"
            )
        with col2:
            # Download transformation recipe as JSON
            import json
            recipe_json = json.dumps(st.session_state['transformations_log'], indent=2, default=str)
            st.download_button(
                "📥 Download Recipe (JSON)",
                recipe_json,
                "transformation_recipe.json",
                "application/json",
                width="stretch"
            )
    else:
        st.info("💡 Apply skewness transformations in the 'Skewness' tab to generate code")
    
    st.markdown("---")
    
    # AI Training Code
    st.markdown("#### 🧠 AI Model Training Code")
    st.caption("Use this code to replicate the anomaly detection model in your own environment.")
    
    ai_code = generate_ai_training_code(col_types['numeric'], settings['ai_sensitivity'])
    st.code(ai_code, language='python')
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Training Script",
            ai_code,
            "train_model.py",
            "text/plain",
            width="stretch"
        )


def generate_skewness_code(transformations_log):
    """
    Generate Python code to replicate skewness transformations
    
    Args:
        transformations_log: List of transformation records from session state
    
    Returns:
        str: Python code as string
    """
    
    code_lines = [
        '"""',
        'Skewness Transformation Script',
        'Auto-generated from Smart CSV AI Studio',
        'Apply these transformations to normalize your data distribution',
        '"""',
        '',
        'import pandas as pd',
        'import numpy as np',
        'from scipy import stats',
        '',
        '',
        'def apply_transformations(df):',
        '    """',
        '    Apply skewness transformations to the dataframe',
        '    ',
        '    Args:',
        '        df: Input pandas DataFrame',
        '    ',
        '    Returns:',
        '        df: Transformed DataFrame',
        '    """',
        '    df = df.copy()  # Create a copy to avoid modifying original',
        '    ',
    ]
    
    # Group transformations by method for cleaner code
    for transform in transformations_log:
        column = transform['column']
        method = transform['method']
        shift = transform.get('shift', 0)
        
        code_lines.append(f"    # Transform '{column}' using {method}")
        code_lines.append(f"    # Original skewness: {transform['original_skew']:.3f} → New: {transform['new_skew']:.3f}")
        
        if "Log" in method:
            if shift > 0:
                code_lines.append(f"    df['{column}'] = np.log1p(df['{column}'] + {shift:.2f})")
            else:
                code_lines.append(f"    df['{column}'] = np.log1p(df['{column}'])")
        
        elif "Square Root" in method:
            if shift > 0:
                code_lines.append(f"    df['{column}'] = np.sqrt(df['{column}'] + {shift:.2f})")
            else:
                code_lines.append(f"    df['{column}'] = np.sqrt(df['{column}'])")
        
        elif "Cube Root" in method:
            code_lines.append(f"    df['{column}'] = np.cbrt(df['{column}'])")
        
        elif "Box-Cox" in method:
            if shift > 0:
                code_lines.append(f"    df['{column}'], _ = stats.boxcox(df['{column}'] + {shift:.2f})")
            else:
                code_lines.append(f"    df['{column}'], _ = stats.boxcox(df['{column}'])")
        
        elif "Yeo-Johnson" in method:
            code_lines.append(f"    df['{column}'], _ = stats.yeojohnson(df['{column}'])")
        
        elif "Reciprocal" in method:
            code_lines.append(f"    df['{column}'] = 1 / df['{column}']")
        
        code_lines.append("")
    
    code_lines.extend([
        '    return df',
        '',
        '',
        'if __name__ == "__main__":',
        '    # Load your data',
        '    df = pd.read_csv("your_data.csv")',
        '    ',
        '    print("Original data shape:", df.shape)',
        '    print("\\nOriginal skewness:")',
        '    print(df.select_dtypes(include=[np.number]).skew())',
        '    ',
        '    # Apply transformations',
        '    df_transformed = apply_transformations(df)',
        '    ',
        '    print("\\nTransformed skewness:")',
        '    print(df_transformed.select_dtypes(include=[np.number]).skew())',
        '    ',
        '    # Save transformed data',
        '    df_transformed.to_csv("data_transformed.csv", index=False)',
        '    print("\\n✅ Transformations applied and saved to data_transformed.csv")',
    ])
    
    return '\n'.join(code_lines)