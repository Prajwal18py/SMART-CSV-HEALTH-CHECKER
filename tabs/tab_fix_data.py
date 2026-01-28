"""
Tab 3: Fix Data
Auto-cleaning, AI repair, wizard, and interactive editor
"""
import streamlit as st
import pandas as pd
import numpy as np
from features.imputation import ai_smart_imputation


def render_fix_data_tab(df, results, col_types):
    """Render the complete Fix Data tab with all features"""
    
    st.subheader("🛠️ Auto-Clean Your Data")
    
    # =================================================================
    # AI AUTO-REPAIR
    # =================================================================
    with st.expander("🤖 AI Auto-Repair (Experimental)", expanded=False):
        st.caption("Uses Random Forest to predict and fill missing values based on patterns in other columns.")
        
        if st.button("🚀 Run AI Repair"):
            with st.spinner("🧠 AI analyzing patterns..."):
                progress = st.progress(0)
                df_repaired = df.copy()
                repaired_cols = []
                cols_with_missing = [c for c in df.columns if df[c].isna().sum() > 0]
                
                for idx, col in enumerate(cols_with_missing):
                    df_repaired = ai_smart_imputation(df_repaired, col)
                    repaired_cols.append(col)
                    progress.progress((idx + 1) / len(cols_with_missing))
                
                progress.empty()
                
                if repaired_cols:
                    st.success(f"✨ Repaired {len(repaired_cols)} columns: {', '.join(repaired_cols)}")
                    st.dataframe(df_repaired.head(20))
                else:
                    st.info("✅ Data is already complete!")
    
    # =================================================================
    # SMART CLEANING WIZARD
    # =================================================================
    st.markdown("---")
    st.markdown('<h2 class="gradient-header">🔮 Smart Cleaning Wizard</h2>', unsafe_allow_html=True)
    st.caption("Let the wizard guide you through cleaning step-by-step")
    
    # Initialize session state
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 0
    if 'wizard_actions' not in st.session_state:
        st.session_state.wizard_actions = {}
    
    # Step 0: Start button
    if st.session_state.wizard_step == 0:
        if st.button("🪄 Start Cleaning Wizard", type="primary", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    
    # Steps 1-4: Wizard flow
    elif st.session_state.wizard_step > 0:
        steps = ["Missing Data", "Duplicates", "Outliers", "Summary"]
        current_step = st.session_state.wizard_step
        
        # Progress indicator
        cols_prog = st.columns(len(steps))
        for idx, step in enumerate(steps):
            with cols_prog[idx]:
                if idx + 1 < current_step:
                    st.markdown(f"✅ **{step}**")
                elif idx + 1 == current_step:
                    st.markdown(f"🔵 **{step}**")
                else:
                    st.markdown(f"⚪ {step}")
        
        st.progress(current_step / len(steps))
        st.markdown("---")
        
        # STEP 1: Missing Data
        if current_step == 1:
            st.markdown("### Step 1: Handle Missing Values")
            missing_cols = df.columns[df.isna().any()].tolist()
            
            if missing_cols:
                for col in missing_cols[:5]:
                    act = st.selectbox(
                        f"Action for {col}",
                        ["Skip", "Fill Mean", "Fill Mode", "Drop Column"],
                        key=f"wiz_{col}"
                    )
                    st.session_state.wizard_actions[col] = act
            else:
                st.success("✅ No missing values found!")
            
            if st.button("Next: Duplicates →"):
                st.session_state.wizard_step = 2
                st.rerun()
        
        # STEP 2: Duplicates
        elif current_step == 2:
            st.markdown("### Step 2: Remove Duplicates")
            dup_count = df.duplicated().sum()
            
            if dup_count > 0:
                st.warning(f"Found {dup_count} duplicates.")
                st.session_state.wizard_actions['dedup'] = st.checkbox("Remove Duplicates?", value=True)
            else:
                st.success("✅ No duplicates found!")
            
            if st.button("Next: Outliers →"):
                st.session_state.wizard_step = 3
                st.rerun()
        
        # STEP 3: Outliers
        elif current_step == 3:
            st.markdown("### Step 3: Handle Outliers")
            
            if not results['stats']['outlier_info'].empty:
                st.dataframe(results['stats']['outlier_info'])
                st.session_state.wizard_actions['outliers'] = st.radio(
                    "Handle Outliers?",
                    ["Keep", "Remove Rows"]
                )
            else:
                st.success("✅ No significant outliers detected!")
            
            if st.button("Finish & Apply →"):
                st.session_state.wizard_step = 4
                st.rerun()
        
        # STEP 4: Summary & Apply
        elif current_step == 4:
            st.markdown("### ✅ Ready to Apply")
            
            # Show summary
            st.markdown("**Actions to be performed:**")
            for key, val in st.session_state.wizard_actions.items():
                if val not in ["Skip", False]:
                    st.info(f"• {key}: {val}")
            
            if st.button("✨ Apply All Changes", type="primary"):
                df_clean = df.copy()
                
                # Step 1: Handle missing values
                for col, act in st.session_state.wizard_actions.items():
                    if col in df_clean.columns:
                        if act == "Fill Mean" and pd.api.types.is_numeric_dtype(df_clean[col]):
                            df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                        elif act == "Fill Mode":
                            mode_vals = df_clean[col].mode()
                            if not mode_vals.empty:
                                df_clean[col].fillna(mode_vals[0], inplace=True)
                        elif act == "Drop Column":
                            df_clean.drop(columns=[col], inplace=True)
                
                # Step 2: Remove duplicates
                if st.session_state.wizard_actions.get('dedup'):
                    df_clean.drop_duplicates(inplace=True)
                
                # Step 3: Handle outliers
                if st.session_state.wizard_actions.get('outliers') == "Remove Rows":
                    for col in df_clean.select_dtypes(include=[np.number]).columns:
                        Q1, Q3 = df_clean[col].quantile(0.25), df_clean[col].quantile(0.75)
                        IQR = Q3 - Q1
                        df_clean = df_clean[
                            ~((df_clean[col] < (Q1 - 1.5 * IQR)) |
                              (df_clean[col] > (Q3 + 1.5 * IQR)))
                        ]
                
                st.toast("Changes applied successfully!", icon="✨")
                st.success(
                    f"✅ Cleaned! {len(df)} → {len(df_clean)} rows "
                    f"({len(df) - len(df_clean)} removed)"
                )
                st.dataframe(df_clean.head(20))
                
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    df_clean.to_csv(index=False).encode('utf-8'),
                    "wizard_cleaned.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            # Reset wizard
            if st.button("🔄 Start New Wizard"):
                st.session_state.wizard_step = 0
                st.session_state.wizard_actions = {}
                st.rerun()
    
    # =================================================================
    # MANUAL CLEANING OPTIONS
    # =================================================================
    st.markdown("---")
    
    cleaning_ops = {}
    c1, c2 = st.columns(2)
    
    with c1:
        dup_count = df.duplicated().sum()
        cleaning_ops['drop_duplicates'] = st.checkbox(
            f"🗑️ Remove Duplicates ({dup_count})",
            value=(dup_count > 0)
        )
        
        high_miss = [c for c in df.columns if df[c].isna().mean() > 0.5]
        if high_miss:
            cleaning_ops['drop_cols'] = st.multiselect(
                "❌ Drop Columns (>50% Missing)",
                high_miss,
                default=high_miss
            )
    
    with c2:
        cleaning_ops['impute_mean'] = st.multiselect(
            "🔢 Fill Numeric (Mean)",
            col_types['numeric']
        )
        cleaning_ops['impute_mode'] = st.multiselect(
            "📝 Fill Categorical (Mode)",
            col_types['categorical']
        )
    
    # Apply auto-cleaning preview
    df_clean_preview = df.copy()
    
    if cleaning_ops.get('drop_duplicates'):
        df_clean_preview.drop_duplicates(inplace=True)
    
    if cleaning_ops.get('drop_cols'):
        df_clean_preview.drop(columns=cleaning_ops['drop_cols'], inplace=True)
    
    for c in cleaning_ops.get('impute_mean', []):
        df_clean_preview[c] = df_clean_preview[c].fillna(df_clean_preview[c].mean())
    
    for c in cleaning_ops.get('impute_mode', []):
        if len(df_clean_preview[c].mode()) > 0:
            df_clean_preview[c] = df_clean_preview[c].fillna(df_clean_preview[c].mode()[0])
    
    st.write("")
    st.markdown("---")
    
    # =================================================================
    # INTERACTIVE DATA EDITOR
    # =================================================================
    st.markdown('<h3 class="gradient-header">✏️ Interactive Data Editor</h3>', unsafe_allow_html=True)
    st.caption("Double-click on any cell below to manually fix typos or values.")
    
    edited_df = st.data_editor(
        df_clean_preview,
        num_rows="dynamic",
        height=400,
        key="data_editor"
    )
    
    st.write("")
    
    # Save buttons
    col_reset, col_save = st.columns([1, 3])
    
    with col_reset:
        if st.button("🔄 Reset to Original", help="Undo all manual edits", use_container_width=True):
            st.rerun()
    
    with col_save:
        if st.button("✨ Save Changes & Download Cleaned Data", type="primary", use_container_width=True):
            st.session_state['cleaning_ops'] = cleaning_ops
            
            ops_count = (
                len(cleaning_ops.get('drop_cols', [])) +
                len(cleaning_ops.get('impute_mean', [])) +
                len(cleaning_ops.get('impute_mode', []))
            )
            if cleaning_ops.get('drop_duplicates'):
                ops_count += 1
            
            st.toast("Data cleaned and saved successfully!", icon="✨")
            st.success(f"✅ Auto-cleaned {ops_count} issues + saved manual edits!")
            
            st.download_button(
                "⬇️ Download Cleaned CSV",
                edited_df.to_csv(index=False).encode('utf-8'),
                "cleaned_data.csv",
                "text/csv",
                use_container_width=True
            )