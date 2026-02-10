"""
Tab 3: Fix Data
Auto-cleaning, AI repair, wizard, and interactive editor with comprehensive outlier handling
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
from features.imputation import ai_smart_imputation

def render_fix_data_tab(df, results, col_types, sidebar_settings):
    """
    Render the complete Fix Data tab with all features.
    """
    
    st.subheader("🛠️ Auto-Clean Your Data")
    
    # ✨ WORKFLOW GUIDANCE BANNER
    st.info(
        "💡 **Recommended Workflow:** Clean your data here → Then visit the **📐 Skewness tab** to normalize distributions → Finally check **📊 Visualizations** and **📉 PCA** tabs!",
        icon="🚀"
    )
    st.markdown("---")
    
    # Extract settings from sidebar
    imputation_method = sidebar_settings.get('imputation_method', 'mean')
    outlier_sensitivity = sidebar_settings.get('outlier_sensitivity', 1.5)
    
    # Initialize session state for global cleaned data if not exists
    if 'global_cleaned_df' not in st.session_state:
        st.session_state.global_cleaned_df = None

    # =================================================================
    # 🎯 OUTLIER DETECTION ALERT
    # =================================================================
    # Count outliers using IQR method
    outlier_count = 0
    outlier_cols = []
    
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[((df[col] < (Q1 - outlier_sensitivity * IQR)) | 
                       (df[col] > (Q3 + outlier_sensitivity * IQR)))]
        if len(outliers) > 0:
            outlier_count += len(outliers)
            outlier_cols.append(col)
    
    if outlier_count > 0:
        st.warning(
            f"⚠️ **{outlier_count} outlier(s) detected across {len(outlier_cols)} column(s)!** "
            f"Use the **Smart Cleaning Wizard** below or the **Manual Outlier Treatment** section to handle them.",
            icon="📊"
        )
    
    # =================================================================
    # ⚡ GLOBAL STRATEGY DASHBOARD (Redesigned)
    # =================================================================
    with st.container():
        # 1. Status Banner
        st.info(f"⚙️ **Active Strategy:** You selected **'{imputation_method.upper()}'** in the Sidebar.", icon="ℹ️")
        st.caption("⚠️ **Note:** This strategy handles missing values only. Outliers require separate treatment below.")
        
        # 2. Action Row (Text + Button)
        c_text, c_btn = st.columns([0.7, 0.3], gap="medium")
        
        with c_text:
            st.markdown(f"### Apply **{imputation_method.upper()}**?")
            st.caption(f"This will immediately process all missing values using the {imputation_method} method.")
        
        with c_btn:
            st.write("") # Spacer to align button vertically
            apply_btn = st.button(
                f"⚡ Apply {imputation_method.upper()} Now", 
                type="primary", 
                width="stretch"
            )

        # 3. Processing Logic (Uses st.status instead of spinner)
        if apply_btn:
            cols_missing = [c for c in df.columns if df[c].isna().sum() > 0]
            
            if not cols_missing:
                st.toast("✅ Data is already complete!", icon="✨")
                st.success("✅ Data is already complete! No imputation needed.")
            else:
                # MODERN LOADING UI
                with st.status(f"🚀 Running {imputation_method.upper()} Imputation...", expanded=True) as status:
                    df_global = df.copy()
                    
                    # Track operations for code generation
                    cleaning_operations = {
                        'method': imputation_method,
                        'impute_mean': [],
                        'impute_mode': [],
                        'impute_mice': [],
                        'drop_rows': False
                    }
                    
                    st.write("🔍 Analyzing missing patterns...")
                    time.sleep(0.5) # UX pause to let user see the step
                    
                    if imputation_method == 'mice':
                        st.write("🧠 Training AI models for imputation...")
                        for col in cols_missing:
                            df_global = ai_smart_imputation(df_global, col)
                            cleaning_operations['impute_mice'].append(col)
                        
                    elif imputation_method == 'drop':
                        st.write("🗑️ Removing incomplete rows...")
                        df_global = df_global.dropna()
                        cleaning_operations['drop_rows'] = True
                        
                    else: # Mean/Mode
                        st.write("📊 Calculating statistical averages...")
                        for col in cols_missing:
                            if pd.api.types.is_numeric_dtype(df_global[col]):
                                df_global[col] = df_global[col].fillna(df_global[col].mean())
                                cleaning_operations['impute_mean'].append(col)
                            else:
                                if not df_global[col].mode().empty:
                                    df_global[col] = df_global[col].fillna(df_global[col].mode()[0])
                                    cleaning_operations['impute_mode'].append(col)
                    
                    st.write("✨ Finalizing dataset...")
                    time.sleep(0.3)
                    status.update(label="✅ Imputation Complete!", state="complete", expanded=False)
                    
                    # Save to session state so it persists
                    st.session_state.global_cleaned_df = df_global
                    # ✅ SAVE OPERATIONS FOR CODE GENERATION
                    st.session_state['cleaning_ops'] = cleaning_operations

        # 4. Results Display (FULL WIDTH - OUTSIDE COLUMNS)
        if st.session_state.global_cleaned_df is not None:
            st.markdown("---")
            
            # Success Metrics
            res_df = st.session_state.global_cleaned_df
            rows_kept = len(res_df)
            rows_orig = len(df)
            
            col_res1, col_res2 = st.columns([3, 1])
            
            with col_res1:
                st.success(f"✅ **Success!** Data processed using {imputation_method.upper()}.")
                st.markdown(f"**Rows:** {rows_kept} (Original: {rows_orig})")
                if outlier_count > 0:
                    st.warning(f"⚠️ **Note:** {outlier_count} outliers still present. Use wizard or manual section below to handle them.")
            
            with col_res2:
                 st.download_button(
                    label="⬇️ Download CSV",
                    data=res_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"cleaned_data_{imputation_method}.csv",
                    mime="text/csv",
                    width="stretch"
                )

            # Data Preview (Centered and Full Width)
            with st.expander("👀 View Cleaned Data Result", expanded=True):
                st.dataframe(res_df.head(50), height=400)

    st.markdown("---")


    # =================================================================
    # AI AUTO-REPAIR (MICE/Advanced)
    # =================================================================
    # We expand this automatically if MICE is selected in sidebar
    start_expanded = (imputation_method == 'mice')
    
    with st.expander("🤖 AI Auto-Repair (Advanced)", expanded=start_expanded):
        st.caption("Uses Random Forest to predict and fill missing values (Best for MICE preference).")
        st.warning("⚠️ **Note:** This handles missing values only. Outliers require separate treatment below.", icon="ℹ️")
        
        if st.button("🚀 Run AI Repair", key="ai_repair_btn"):
            cols_with_missing = [c for c in df.columns if df[c].isna().sum() > 0]
            
            if not cols_with_missing:
                st.info("✅ No missing values found! Data is already complete.")
            else:
                with st.status("🧠 AI analyzing patterns...", expanded=True) as status:
                    progress = st.progress(0)
                    df_repaired = df.copy()
                    repaired_cols = []
                    
                    for idx, col in enumerate(cols_with_missing):
                        st.write(f"Processing: **{col}**")
                        try:
                            df_repaired = ai_smart_imputation(df_repaired, col)
                            repaired_cols.append(col)
                        except Exception as e:
                            st.warning(f"⚠️ Could not repair '{col}': {str(e)}")
                        progress.progress((idx + 1) / len(cols_with_missing))
                    
                    progress.empty()
                    status.update(label="✅ AI Analysis Complete!", state="complete", expanded=False)
                
                if repaired_cols:
                    st.success(f"✨ Repaired {len(repaired_cols)} columns: {', '.join(repaired_cols)}")
                    if outlier_count > 0:
                        st.warning(f"⚠️ **Note:** {outlier_count} outliers still present. Use wizard or manual section below to handle them.")
                    
                    st.dataframe(df_repaired.head(20))
                    
                    # ✅ SAVE TO SESSION STATE for Skewness tab
                    st.session_state['global_cleaned_df'] = df_repaired
                    
                    # ✅ SAVE OPERATIONS FOR CODE GENERATION
                    st.session_state['cleaning_ops'] = {
                        'method': 'mice',
                        'impute_mice': repaired_cols,
                        'impute_mean': [],
                        'impute_mode': [],
                        'drop_rows': False
                    }
                    
                    # ✨ REMINDER MESSAGE
                    st.info("💡 **Next Step:** Visit the **Skewness tab** to normalize your data distribution!", icon="📐")
                    
                    st.download_button(
                        "⬇️ Download AI-Repaired CSV",
                        df_repaired.to_csv(index=False).encode('utf-8'),
                        "ai_repaired_data.csv",
                        "text/csv",
                        width="stretch",
                        key="download_ai_repaired"
                    )

    # =================================================================
    # SMART CLEANING WIZARD (ENHANCED WITH OUTLIER OPTIONS)
    # =================================================================
    st.markdown("---")
    st.markdown('<h2 class="gradient-header">🔮 Smart Cleaning Wizard</h2>', unsafe_allow_html=True)
    st.caption("Let the wizard guide you through cleaning step-by-step (handles missing data, duplicates, and outliers)")
    
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 0
    if 'wizard_actions' not in st.session_state:
        st.session_state.wizard_actions = {}
    
    if st.session_state.wizard_step == 0:
        if st.button("🪄 Start Cleaning Wizard", type="primary", width="stretch"):
            st.session_state.wizard_step = 1
            st.rerun()
    
    elif st.session_state.wizard_step > 0:
        steps = ["Missing Data", "Duplicates", "Outliers", "Summary"]
        current_step = st.session_state.wizard_step
        
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
            
            # Determine default action based on Sidebar Setting
            default_index = 0  # Skip
            if imputation_method == 'mean':
                default_index = 1 # Fill Mean
            elif imputation_method == 'drop':
                default_index = 3 # Drop Column
            
            if missing_cols:
                for col in missing_cols[:5]:
                    # Adjust default index based on column type + sidebar setting
                    final_index = default_index
                    if imputation_method == 'mean' and not pd.api.types.is_numeric_dtype(df[col]):
                        final_index = 2 # Fill Mode for categorical if 'mean' was selected
                        
                    act = st.selectbox(
                        f"Action for {col}",
                        ["Skip", "Fill Mean", "Fill Mode", "Drop Column"],
                        index=final_index,
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
        
        # STEP 3: Outliers (ENHANCED)
        elif current_step == 3:
            st.markdown("### Step 3: Handle Outliers")
            
            # Count outliers per column
            outlier_details = []
            for col in df.select_dtypes(include=[np.number]).columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers_mask = (df[col] < (Q1 - outlier_sensitivity * IQR)) | (df[col] > (Q3 + outlier_sensitivity * IQR))
                outlier_cnt = outliers_mask.sum()
                
                if outlier_cnt > 0:
                    outlier_details.append({
                        'Column': col,
                        'Outliers': outlier_cnt,
                        'Percentage': f"{outlier_cnt / len(df) * 100:.1f}%"
                    })
            
            if outlier_details:
                st.dataframe(pd.DataFrame(outlier_details), hide_index=True)
                
                st.markdown("#### Choose Outlier Treatment Method:")
                st.session_state.wizard_actions['outlier_method'] = st.radio(
                    "How would you like to handle outliers?",
                    [
                        "Keep all outliers",
                        "Remove outlier rows (IQR method)",
                        "Cap outliers (Winsorize)",
                        "Log transform numeric columns"
                    ],
                    help="• Keep: No changes\n• Remove: Delete rows with outliers\n• Cap: Replace outliers with boundary values\n• Log: Apply log transformation to reduce skew"
                )
                
                # If user chooses cap or log, let them select columns
                if st.session_state.wizard_actions.get('outlier_method') in ["Cap outliers (Winsorize)", "Log transform numeric columns"]:
                    outlier_cols_list = [d['Column'] for d in outlier_details]
                    st.session_state.wizard_actions['outlier_cols'] = st.multiselect(
                        "Select columns to treat:",
                        outlier_cols_list,
                        default=outlier_cols_list
                    )
            else:
                st.success("✅ No significant outliers detected!")
            
            if st.button("Finish & Apply →"):
                st.session_state.wizard_step = 4
                st.rerun()
        
        # STEP 4: Summary & Apply
        elif current_step == 4:
            st.markdown("### ✅ Ready to Apply")
            
            st.markdown("**Actions to be performed:**")
            for key, val in st.session_state.wizard_actions.items():
                if val not in ["Skip", False, "Keep all outliers"]:
                    st.info(f"• {key}: {val}")
            
            if st.button("✨ Apply All Changes", type="primary"):
                df_clean = df.copy()
                
                # Track wizard operations for code generation
                wizard_ops = {
                    'method': 'wizard',
                    'impute_mean': [],
                    'impute_mode': [],
                    'drop_cols': [],
                    'drop_duplicates': False,
                    'outlier_treatment': None,
                    'outlier_cols': []
                }
                
                # Apply missing data actions
                for col, act in st.session_state.wizard_actions.items():
                    if col in df_clean.columns:
                        if act == "Fill Mean" and pd.api.types.is_numeric_dtype(df_clean[col]):
                            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                            wizard_ops['impute_mean'].append(col)
                        elif act == "Fill Mode":
                            mode_vals = df_clean[col].mode()
                            if not mode_vals.empty:
                                df_clean[col] = df_clean[col].fillna(mode_vals[0])
                                wizard_ops['impute_mode'].append(col)
                        elif act == "Drop Column":
                            df_clean = df_clean.drop(columns=[col])
                            wizard_ops['drop_cols'].append(col)
                
                # Apply deduplication
                if st.session_state.wizard_actions.get('dedup'):
                    df_clean = df_clean.drop_duplicates()
                    wizard_ops['drop_duplicates'] = True
                
                # Apply outlier treatment
                outlier_method = st.session_state.wizard_actions.get('outlier_method', 'Keep all outliers')
                
                if outlier_method == "Remove outlier rows (IQR method)":
                    for col in df_clean.select_dtypes(include=[np.number]).columns:
                        Q1, Q3 = df_clean[col].quantile(0.25), df_clean[col].quantile(0.75)
                        IQR = Q3 - Q1
                        df_clean = df_clean[
                            ~((df_clean[col] < (Q1 - outlier_sensitivity * IQR)) |
                              (df_clean[col] > (Q3 + outlier_sensitivity * IQR)))
                        ]
                    wizard_ops['outlier_treatment'] = 'remove'
                
                elif outlier_method == "Cap outliers (Winsorize)":
                    cols_to_cap = st.session_state.wizard_actions.get('outlier_cols', [])
                    for col in cols_to_cap:
                        if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                            Q1, Q3 = df_clean[col].quantile(0.25), df_clean[col].quantile(0.75)
                            IQR = Q3 - Q1
                            lower_bound = Q1 - outlier_sensitivity * IQR
                            upper_bound = Q3 + outlier_sensitivity * IQR
                            df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
                    wizard_ops['outlier_treatment'] = 'cap'
                    wizard_ops['outlier_cols'] = cols_to_cap
                
                elif outlier_method == "Log transform numeric columns":
                    cols_to_log = st.session_state.wizard_actions.get('outlier_cols', [])
                    for col in cols_to_log:
                        if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                            # Ensure positive values for log
                            if (df_clean[col] > 0).all():
                                df_clean[col] = np.log1p(df_clean[col])
                            else:
                                st.warning(f"⚠️ Skipped log transform for '{col}' (contains non-positive values)")
                    wizard_ops['outlier_treatment'] = 'log'
                    wizard_ops['outlier_cols'] = cols_to_log
                
                # ✅ SAVE TO SESSION STATE for Skewness tab
                st.session_state['global_cleaned_df'] = df_clean
                
                # ✅ SAVE OPERATIONS FOR CODE GENERATION
                st.session_state['cleaning_ops'] = wizard_ops
                
                st.toast("Changes applied successfully!", icon="✨")
                st.success(
                    f"✅ Cleaned! {len(df)} → {len(df_clean)} rows "
                    f"({len(df) - len(df_clean)} removed)"
                )
                st.dataframe(df_clean.head(20))
                
                # ✨ REMINDER MESSAGE
                st.info("💡 **Next Step:** Visit the **Skewness tab** to normalize your data distribution!", icon="📐")
                
                st.download_button(
                    "⬇️ Download Cleaned CSV",
                    df_clean.to_csv(index=False).encode('utf-8'),
                    "wizard_cleaned.csv",
                    "text/csv",
                    width="stretch"
                )
            
            if st.button("🔄 Start New Wizard"):
                st.session_state.wizard_step = 0
                st.session_state.wizard_actions = {}
                st.rerun()

    # =================================================================
    # MANUAL OUTLIER TREATMENT SECTION (NEW)
    # =================================================================
    st.markdown("---")
    st.markdown('<h3 class="gradient-header">🎯 Manual Outlier Treatment</h3>', unsafe_allow_html=True)
    st.caption("Fine-tune outlier handling for specific columns")
    
    with st.expander("🔧 Configure Outlier Treatment", expanded=False):
        # Select columns for outlier treatment
        numeric_cols = col_types['numeric']
        
        if numeric_cols:
            outlier_treat_cols = st.multiselect(
                "📊 Select numeric columns to treat for outliers:",
                numeric_cols,
                help="Choose columns where you want to detect and handle outliers"
            )
            
            if outlier_treat_cols:
                # Method selector
                outlier_treat_method = st.selectbox(
                    "🛠️ Treatment method:",
                    [
                        "Remove outlier rows (IQR method)",
                        "Cap outliers (Winsorize)",
                        "Log transform",
                        "Square root transform",
                        "Z-score filter (remove beyond threshold)"
                    ],
                    help="Different methods for handling outliers"
                )
                
                # Sensitivity/threshold slider
                col_slider1, col_slider2 = st.columns(2)
                
                with col_slider1:
                    if "Z-score" in outlier_treat_method:
                        threshold = st.slider(
                            "Z-score threshold:",
                            1.0, 4.0, 3.0, 0.5,
                            help="Remove values beyond this many standard deviations from mean"
                        )
                    else:
                        threshold = st.slider(
                            "IQR multiplier:",
                            1.0, 3.0, outlier_sensitivity, 0.5,
                            help="Higher = more lenient (fewer outliers detected)"
                        )
                
                with col_slider2:
                    # Show preview of how many outliers will be affected
                    preview_count = 0
                    for col in outlier_treat_cols:
                        if col in df.columns:
                            if "Z-score" in outlier_treat_method:
                                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                                preview_count += (z_scores > threshold).sum()
                            else:
                                Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                                IQR = Q3 - Q1
                                outliers = (df[col] < (Q1 - threshold * IQR)) | (df[col] > (Q3 + threshold * IQR))
                                preview_count += outliers.sum()
                    
                    st.metric(
                        "Outliers to treat:",
                        preview_count,
                        help="Number of outlier values that will be affected"
                    )
                
                # Apply button
                if st.button("⚡ Apply Outlier Treatment", type="primary", width="stretch"):
                    df_outlier_clean = df.copy()
                    
                    # Track operations
                    outlier_ops = {
                        'method': 'manual_outlier',
                        'treatment': outlier_treat_method,
                        'columns': outlier_treat_cols,
                        'threshold': threshold
                    }
                    
                    with st.status("🔧 Treating outliers...", expanded=True) as status:
                        if outlier_treat_method == "Remove outlier rows (IQR method)":
                            for col in outlier_treat_cols:
                                if col in df_outlier_clean.columns:
                                    Q1, Q3 = df_outlier_clean[col].quantile(0.25), df_outlier_clean[col].quantile(0.75)
                                    IQR = Q3 - Q1
                                    df_outlier_clean = df_outlier_clean[
                                        ~((df_outlier_clean[col] < (Q1 - threshold * IQR)) |
                                          (df_outlier_clean[col] > (Q3 + threshold * IQR)))
                                    ]
                        
                        elif outlier_treat_method == "Cap outliers (Winsorize)":
                            for col in outlier_treat_cols:
                                if col in df_outlier_clean.columns:
                                    Q1, Q3 = df_outlier_clean[col].quantile(0.25), df_outlier_clean[col].quantile(0.75)
                                    IQR = Q3 - Q1
                                    lower_bound = Q1 - threshold * IQR
                                    upper_bound = Q3 + threshold * IQR
                                    df_outlier_clean[col] = df_outlier_clean[col].clip(lower=lower_bound, upper=upper_bound)
                        
                        elif outlier_treat_method == "Log transform":
                            for col in outlier_treat_cols:
                                if col in df_outlier_clean.columns:
                                    if (df_outlier_clean[col] > 0).all():
                                        df_outlier_clean[col] = np.log1p(df_outlier_clean[col])
                                    else:
                                        st.warning(f"⚠️ Skipped '{col}' (contains non-positive values)")
                        
                        elif outlier_treat_method == "Square root transform":
                            for col in outlier_treat_cols:
                                if col in df_outlier_clean.columns:
                                    if (df_outlier_clean[col] >= 0).all():
                                        df_outlier_clean[col] = np.sqrt(df_outlier_clean[col])
                                    else:
                                        st.warning(f"⚠️ Skipped '{col}' (contains negative values)")
                        
                        elif "Z-score" in outlier_treat_method:
                            for col in outlier_treat_cols:
                                if col in df_outlier_clean.columns:
                                    z_scores = np.abs((df_outlier_clean[col] - df_outlier_clean[col].mean()) / df_outlier_clean[col].std())
                                    df_outlier_clean = df_outlier_clean[z_scores <= threshold]
                        
                        status.update(label="✅ Outlier treatment complete!", state="complete", expanded=False)
                    
                    # Save results
                    st.session_state['global_cleaned_df'] = df_outlier_clean
                    st.session_state['cleaning_ops'] = outlier_ops
                    
                    rows_removed = len(df) - len(df_outlier_clean)
                    st.success(f"✅ Treatment applied! {rows_removed} rows affected.")
                    
                    # Show preview
                    st.dataframe(df_outlier_clean.head(20))
                    
                    # Download button
                    st.download_button(
                        "⬇️ Download Outlier-Treated CSV",
                        df_outlier_clean.to_csv(index=False).encode('utf-8'),
                        "outlier_treated_data.csv",
                        "text/csv",
                        width="stretch"
                    )
        else:
            st.info("ℹ️ No numeric columns available for outlier treatment.")

    # =================================================================
    # MANUAL CLEANING OPTIONS
    # =================================================================
    st.markdown("---")
    st.markdown('<h3 class="gradient-header">🔧 Manual Cleaning Options</h3>', unsafe_allow_html=True)
    
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
        # Default numeric/categorical selections based on Sidebar Strategy
        default_mean = []
        default_mode = []
        
        if imputation_method == 'mean':
            default_mean = col_types['numeric']
            default_mode = col_types['categorical']

        cleaning_ops['impute_mean'] = st.multiselect(
            "🔢 Fill Numeric (Mean)",
            col_types['numeric'],
            default=default_mean
        )
        cleaning_ops['impute_mode'] = st.multiselect(
            "📝 Fill Categorical (Mode)",
            col_types['categorical'],
            default=default_mode
        )
    
    df_clean_preview = df.copy()
    
    # Apply preview logic
    if cleaning_ops.get('drop_duplicates'):
        df_clean_preview = df_clean_preview.drop_duplicates()
    
    if cleaning_ops.get('drop_cols'):
        df_clean_preview = df_clean_preview.drop(columns=cleaning_ops['drop_cols'])
    
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
    
    col_reset, col_save = st.columns([1, 3])
    
    with col_reset:
        if st.button("🔄 Reset to Original", help="Undo all manual edits", width="stretch"):
            st.rerun()
    
    with col_save:
        if st.button("✨ Save Changes & Download Cleaned Data", type="primary", width="stretch"):
            # ✅ SAVE TO SESSION STATE for Skewness tab
            st.session_state['global_cleaned_df'] = edited_df
            
            # ✅ SAVE OPERATIONS FOR CODE GENERATION
            cleaning_ops['method'] = 'manual'
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
            
            # ✨ REMINDER MESSAGE
            st.info("💡 **Next Step:** Visit the **Skewness tab** to normalize your data distribution!", icon="📐")
            
            st.download_button(
                "⬇️ Download Cleaned CSV",
                edited_df.to_csv(index=False).encode('utf-8'),
                "cleaned_data.csv",
                "text/csv",
                width="stretch"
            )