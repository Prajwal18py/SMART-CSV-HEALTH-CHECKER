"""
Tab 3: Fix Data
Auto-cleaning, AI repair, wizard, and interactive editor with comprehensive outlier handling
"""
import streamlit as st
import pandas as pd
import numpy as np
import time
from features.imputation import ai_smart_imputation
from utils.export_utils import smart_download_button, get_format_label

# ══════════════════════════════════════════════════════════════════════
# ENHANCED CSS - MATCHING EDA STYLE
# ══════════════════════════════════════════════════════════════════════
FIX_DATA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* Section headers matching EDA */
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
.eda-section-head .count {
    margin-left: auto;
    background: rgba(99,102,241,.2);
    color: #a5b4fc;
    border-radius: 20px;
    padding: .15rem .6rem;
    font-size: .72rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

/* Alert cards */
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

/* Info/Status cards */
.status-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: border-color .25s, box-shadow .25s, transform .25s;
}
.status-card:hover {
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

/* Data editor */
[data-testid="stDataFrameResizable"] {
    transition: box-shadow 0.3s ease;
}
[data-testid="stDataFrameResizable"]:hover {
    box-shadow: 0 4px 16px rgba(99,102,241,.15);
}
</style>
"""

def render_fix_data_tab(df_original, results, col_types, sidebar_settings):
    """
    Render the Fix Data tab.
    ✨ NOW READS: anomaly_cleaned_df if available
    """
    st.markdown(FIX_DATA_CSS, unsafe_allow_html=True)
    
    fmt_label = get_format_label()
    
    st.subheader("🛠️ Auto-Clean Your Data")
    
    # ✨ SMART DATA SOURCE: Use anomaly-cleaned data if available
    df = df_original  # Default
    data_source_label = "Original"
    
    if st.session_state.get('anomaly_cleaned_df') is not None:
        df = st.session_state['anomaly_cleaned_df']
        data_source_label = "Anomaly-Free (from AI Deep Dive)"
        
        st.success(
            f"✅ Using **{data_source_label}** data — anomalies already removed! "
            f"Now clean missing values, duplicates & outliers below.",
            icon="🎯"
        )
    else:
        st.info(
            "ℹ️ Using **Original** data. Visit **AI Deep Dive** first to remove anomalies, "
            "then return here for final cleaning.",
            icon="💡"
        )
    
    # ✨ WORKFLOW GUIDANCE BANNER
    st.info(
        "💡 **Recommended Workflow:** AI Deep Dive (remove anomalies) → Fix Data (clean remaining issues) → "
        "EDA → Skewness → Feature Engineering → Model Builder",
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
            st.write("")
            apply_btn = st.button(
                f"⚡ Apply {imputation_method.upper()} Now", 
                type="primary"
            )

        # 3. Processing Logic
        if apply_btn:
            cols_missing = [c for c in df.columns if df[c].isna().sum() > 0]
            
            if not cols_missing:
                st.toast("✅ Data is already complete!", icon="✨")
                st.success("✅ Data is already complete! No imputation needed.")
            else:
                with st.status(f"🚀 Running {imputation_method.upper()} Imputation...", expanded=True) as status:
                    df_global = df.copy()
                    
                    cleaning_operations = {
                        'method': imputation_method,
                        'impute_mean': [],
                        'impute_mode': [],
                        'impute_mice': [],
                        'drop_rows': False
                    }
                    
                    st.write("🔍 Analyzing missing patterns...")
                    time.sleep(0.5)
                    
                    if imputation_method == 'mice':
                        st.write("🧠 Training AI models for imputation...")
                        for col in cols_missing:
                            df_global = ai_smart_imputation(df_global, col)
                            cleaning_operations['impute_mice'].append(col)
                        
                    elif imputation_method == 'drop':
                        st.write("🗑️ Removing incomplete rows...")
                        df_global = df_global.dropna()
                        cleaning_operations['drop_rows'] = True
                        
                    else:
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
                    
                    st.session_state.global_cleaned_df = df_global
                    st.session_state['cleaning_ops'] = cleaning_operations

        # 4. Results Display
        if st.session_state.global_cleaned_df is not None:
            st.markdown("---")
            
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
                smart_download_button(
                    res_df,
                    label=f"⬇️ Download {fmt_label}",
                    suffix=f"cleaned_{imputation_method}",
                    key="dl_global_strategy",
                    button_width='stretch'
                )

            with st.expander("👀 View Cleaned Data Result", expanded=True):
                st.dataframe(res_df.head(50), height=400)

    st.markdown("---")

    # =================================================================
    # AI AUTO-REPAIR
    # =================================================================
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
                    
                    st.session_state['global_cleaned_df'] = df_repaired
                    st.session_state['cleaning_ops'] = {
                        'method': 'mice',
                        'impute_mice': repaired_cols,
                        'impute_mean': [],
                        'impute_mode': [],
                        'drop_rows': False
                    }
                    
                    st.info("💡 **Next Steps:** Skewness → Feature Engineering → Model Builder. "
                            "Use Imbalanced Data tab if you discover class imbalance after training.",
                            icon="📐")
                    
                    smart_download_button(
                        df_repaired,
                        label=f"⬇️ Download AI-Repaired {fmt_label}",
                        suffix="ai_repaired",
                        key="dl_ai_repaired",
                        button_width='stretch'
                    )

    # =================================================================
    # SMART CLEANING WIZARD
    # =================================================================
    st.markdown("---")
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🔮</span>
        <p class="title">Smart Cleaning Wizard</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Let the wizard guide you through cleaning step-by-step (handles missing data, duplicates, and outliers)")
    
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 0
    if 'wizard_actions' not in st.session_state:
        st.session_state.wizard_actions = {}
    
    if st.session_state.wizard_step == 0:
        if st.button("🪄 Start Cleaning Wizard", type="primary"):
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
            
            default_index = 0
            if imputation_method == 'mean':
                default_index = 1
            elif imputation_method == 'drop':
                default_index = 3
            
            if missing_cols:
                for col in missing_cols[:5]:
                    final_index = default_index
                    if imputation_method == 'mean' and not pd.api.types.is_numeric_dtype(df[col]):
                        final_index = 2
                        
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
        
        # STEP 3: Outliers
        elif current_step == 3:
            st.markdown("### Step 3: Handle Outliers")
            
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
                            if (df_clean[col] > 0).all():
                                df_clean[col] = np.log1p(df_clean[col])
                            else:
                                st.warning(f"⚠️ Skipped log transform for '{col}' (contains non-positive values)")
                    wizard_ops['outlier_treatment'] = 'log'
                    wizard_ops['outlier_cols'] = cols_to_log
                
                st.session_state['global_cleaned_df'] = df_clean
                st.session_state['cleaning_ops'] = wizard_ops
                
                st.toast("Changes applied successfully!", icon="✨")
                st.success(
                    f"✅ Cleaned! {len(df)} → {len(df_clean)} rows "
                    f"({len(df) - len(df_clean)} removed)"
                )
                st.dataframe(df_clean.head(20))
                
                st.info("💡 **Next Step:** Visit the **Skewness tab** to normalize your data distribution!", icon="📐")
                
                smart_download_button(
                    df_clean,
                    label=f"⬇️ Download Cleaned {fmt_label}",
                    suffix="wizard_cleaned",
                    key="dl_wizard",
                    button_width='stretch'
                )
            
            if st.button("🔄 Start New Wizard"):
                st.session_state.wizard_step = 0
                st.session_state.wizard_actions = {}
                st.rerun()

    # =================================================================
    # MANUAL OUTLIER TREATMENT
    # =================================================================
    st.markdown("---")
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🎯</span>
        <p class="title">Manual Outlier Treatment</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Fine-tune outlier handling for specific columns")
    
    with st.expander("🔧 Configure Outlier Treatment", expanded=False):
        numeric_cols = col_types['numeric']
        
        if numeric_cols:
            # Show method selector FIRST
            outlier_treat_method = st.selectbox(
                "🛠️ Treatment method:",
                [
                    "Remove AI-detected anomalies",  # ← First option, doesn't need column selection
                    "Remove outlier rows (IQR method)",
                    "Cap outliers (Winsorize)",
                    "Log transform",
                    "Square root transform",
                    "Z-score filter (remove beyond threshold)"
                ],
                help="AI anomalies are detected in the AI Deep Dive tab. Other methods work on selected columns."
            )
            
            # Column selection only needed for non-AI methods
            if outlier_treat_method != "Remove AI-detected anomalies":
                outlier_treat_cols = st.multiselect(
                    "📊 Select numeric columns to treat for outliers:",
                    numeric_cols,
                    help="Choose columns where you want to detect and handle outliers"
                )
            else:
                outlier_treat_cols = []  # Not needed for AI anomalies
            
            # Show sliders and preview only for methods that need them
            if outlier_treat_cols or outlier_treat_method == "Remove AI-detected anomalies":
                
                col_slider1, col_slider2 = st.columns(2)
                
                with col_slider1:
                    if outlier_treat_method == "Remove AI-detected anomalies":
                        # Show info about AI anomalies instead of slider
                        if 'results' in st.session_state and 'stats' in st.session_state['results']:
                            stats = st.session_state['results']['stats']
                            if 'ai_anomalies' in stats and stats['ai_anomalies'] is not None:
                                anomaly_count = len(stats['ai_anomalies']['indices'])
                                st.info(f"ℹ️ {anomaly_count} AI anomalies detected in AI Deep Dive tab")
                            else:
                                st.warning("⚠️ No AI anomalies found. Run AI Deep Dive first.")
                        else:
                            st.warning("⚠️ No AI analysis found. Run AI Deep Dive first.")
                    elif "Z-score" in outlier_treat_method:
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
                    if outlier_treat_method == "Remove AI-detected anomalies":
                        # Show anomaly count metric
                        if 'results' in st.session_state and 'stats' in st.session_state['results']:
                            stats = st.session_state['results']['stats']
                            if 'ai_anomalies' in stats and stats['ai_anomalies'] is not None:
                                st.metric(
                                    "Anomalies to remove:",
                                    len(stats['ai_anomalies']['indices']),
                                    help="Entire rows will be removed"
                                )
                    else:
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
                
                if st.button("⚡ Apply Outlier Treatment", type="primary"):
                    df_outlier_clean = df.copy()
                    
                    outlier_ops = {
                        'method': 'manual_outlier',
                        'treatment': outlier_treat_method,
                        'columns': outlier_treat_cols,
                        'threshold': threshold
                    }
                    
                    with st.status("🔧 Treating outliers...", expanded=True) as status:
                        # Handle AI anomaly removal
                        if outlier_treat_method == "Remove AI-detected anomalies":
                            # Check if AI analysis has been run
                            if 'results' not in st.session_state or 'stats' not in st.session_state['results']:
                                status.update(label="❌ No analysis found", state="error", expanded=False)
                                st.error(
                                    "❌ No analysis data found. Please visit the **🧠 AI Deep Dive** tab first "
                                    "to run anomaly detection, then return here."
                                )
                                st.stop()
                            
                            stats = st.session_state['results']['stats']
                            
                            if 'ai_anomalies' not in stats or stats['ai_anomalies'] is None:
                                status.update(label="❌ No AI anomalies found", state="error", expanded=False)
                                st.error(
                                    "❌ No AI anomalies detected. Please visit the **🧠 AI Deep Dive** tab first "
                                    "to run anomaly detection."
                                )
                                st.stop()
                            
                            anomaly_indices = stats['ai_anomalies']['indices']
                            
                            if len(anomaly_indices) == 0:
                                status.update(label="✅ No anomalies to remove", state="complete", expanded=False)
                                st.success("✅ No AI anomalies detected in your dataset!")
                                st.stop()
                            
                            st.write(f"🗑️ Removing {len(anomaly_indices)} AI-detected anomalies...")
                            df_outlier_clean = df_outlier_clean.drop(index=anomaly_indices).reset_index(drop=True)
                            st.write(f"   ✓ Removed {len(anomaly_indices)} rows")
                            
                            outlier_ops['treatment'] = 'ai_anomaly_removal'
                            outlier_ops['rows_removed'] = len(anomaly_indices)
                            outlier_ops['columns'] = []  # N/A for AI anomalies
                        
                        elif outlier_treat_method == "Remove outlier rows (IQR method)":
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
                    
                    st.session_state['global_cleaned_df'] = df_outlier_clean
                    st.session_state['cleaning_ops'] = outlier_ops
                    
                    rows_removed = len(df) - len(df_outlier_clean)
                    st.success(f"✅ Treatment applied! {rows_removed} rows affected.")
                    
                    st.dataframe(df_outlier_clean.head(20))
                    
                    smart_download_button(
                        df_outlier_clean,
                        label=f"⬇️ Download Outlier-Treated {fmt_label}",
                        suffix="outlier_treated",
                        key="dl_outlier",
                        button_width='stretch'
                    )
        else:
            st.info("ℹ️ No numeric columns available for outlier treatment.")
    # =================================================================
    # MANUAL CLEANING OPTIONS
    # =================================================================
    st.markdown("---")
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🔧</span>
        <p class="title">Manual Cleaning Options</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">✏️</span>
        <p class="title">Interactive Data Editor</p>
    </div>
    """, unsafe_allow_html=True)
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
        if st.button("🔄 Reset to Original", help="Undo all manual edits"):
            st.rerun()
    
    with col_save:
        if st.button("✨ Save Changes & Download Cleaned Data", type="primary"):
            st.session_state['global_cleaned_df'] = edited_df
            
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
            
            st.info("💡 **Next Step:** Visit the **Skewness tab** to normalize your data distribution!", icon="📐")
            
            smart_download_button(
                edited_df,
                label=f"⬇️ Download Cleaned {fmt_label}",
                suffix="manual_cleaned",
                key="dl_manual",
                button_width='stretch'
            )