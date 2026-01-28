"""
Tab 4: Pipeline Builder
Visual pipeline builder for data cleaning operations
"""
import streamlit as st
import numpy as np
from export.code_generator import generate_pipeline_code


def render_pipeline_tab(df):
    """Render the Pipeline Builder tab"""
    
    st.markdown('<h2 class="gradient-header">🔧 Cleaning Pipeline Builder</h2>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'pipeline_steps' not in st.session_state:
        st.session_state.pipeline_steps = []
    
    c1, c2 = st.columns([1, 3])
    
    # =================================================================
    # LEFT: Add Operations
    # =================================================================
    with c1:
        st.markdown("**Add Operation:**")
        
        # Remove Duplicates button
        if st.button("➕ Remove Duplicates", use_container_width=True):
            st.session_state.pipeline_steps.append({"type": "dedup"})
            st.rerun()
        
        # Fill Missing button
        fill_method = st.selectbox("Fill Method", ["mean", "median", "mode"])
        if st.button("➕ Fill Missing", use_container_width=True):
            st.session_state.pipeline_steps.append({"type": "fill", "method": fill_method})
            st.rerun()
        
        # Drop Column button
        drop_col = st.selectbox("Column to Drop", [""] + list(df.columns))
        if st.button("➕ Drop Column", use_container_width=True, disabled=not drop_col):
            st.session_state.pipeline_steps.append({"type": "drop", "col": drop_col})
            st.rerun()
    
    # =================================================================
    # RIGHT: Pipeline Display & Execution
    # =================================================================
    with c2:
        st.markdown("**Pipeline:**")
        
        if not st.session_state.pipeline_steps:
            st.info("Empty pipeline - add operations from the left")
        else:
            # Display steps
            for i, step in enumerate(st.session_state.pipeline_steps):
                extra = f"({step.get('col', step.get('method', ''))})" if 'col' in step or 'method' in step else ""
                st.markdown(f"**{i+1}.** {step['type']} {extra}")
            
            # Clear pipeline button
            if st.button("🗑️ Clear Pipeline"):
                st.session_state.pipeline_steps = []
                st.rerun()
        
        # Run Pipeline button
        if st.button("▶️ Run Pipeline", type="primary", disabled=len(st.session_state.pipeline_steps) == 0):
            df_pipe = df.copy()
            
            with st.spinner("🔄 Executing pipeline..."):
                for idx, step in enumerate(st.session_state.pipeline_steps):
                    if step['type'] == 'dedup':
                        df_pipe.drop_duplicates(inplace=True)
                    
                    elif step['type'] == 'fill':
                        method = step.get('method', 'mean')
                        num_cols = df_pipe.select_dtypes(include=np.number).columns
                        
                        if method == 'mean':
                            df_pipe[num_cols] = df_pipe[num_cols].fillna(df_pipe[num_cols].mean())
                        elif method == 'median':
                            df_pipe[num_cols] = df_pipe[num_cols].fillna(df_pipe[num_cols].median())
                        elif method == 'mode':
                            for col in num_cols:
                                mode_val = df_pipe[col].mode()
                                if not mode_val.empty:
                                    df_pipe[col].fillna(mode_val[0], inplace=True)
                    
                    elif step['type'] == 'drop':
                        col_to_drop = step.get('col')
                        if col_to_drop and col_to_drop in df_pipe.columns:
                            df_pipe.drop(columns=[col_to_drop], inplace=True)
            
            st.success(
                f"✅ Pipeline Complete! {len(df)} → {len(df_pipe)} rows, "
                f"{len(df.columns)} → {len(df_pipe.columns)} columns"
            )
            
            # Show before/after metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Rows", len(df_pipe), delta=f"{len(df_pipe) - len(df):+,}")
            
            with col2:
                st.metric("Columns", len(df_pipe.columns), delta=f"{len(df_pipe.columns) - len(df.columns):+}")
            
            with col3:
                missing_before = df.isna().sum().sum()
                missing_after = df_pipe.isna().sum().sum()
                st.metric("Missing Values", missing_after, delta=f"{missing_after - missing_before:+,}")
            
            # Preview data
            st.dataframe(df_pipe.head(20))
            
            # Generate code
            code = generate_pipeline_code(st.session_state.pipeline_steps)
            
            with st.expander("📝 View Generated Code"):
                st.code(code, language='python')
            
            # Download buttons
            col_download1, col_download2 = st.columns(2)
            
            with col_download1:
                st.download_button(
                    "📥 Download CSV",
                    df_pipe.to_csv(index=False).encode('utf-8'),
                    "pipeline_output.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col_download2:
                st.download_button(
                    "📥 Download Code",
                    code,
                    "pipeline.py",
                    "text/plain",
                    use_container_width=True
                )