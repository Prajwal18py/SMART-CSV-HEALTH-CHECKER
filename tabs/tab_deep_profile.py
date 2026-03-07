"""
Tab 8: Deep Profile
Custom validation rules, detailed column profiling, and PII detection
NOW WITH: Enhanced UI matching EDA tab design + Centralized PII detection
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from features.pii_detection import detect_pii as detect_pii_features, mask_pii_column
from utils.export_utils import smart_download_button, get_format_label

# ══════════════════════════════════════════════════════════════════════
# ENHANCED CSS - MATCHING EDA TAB
# ══════════════════════════════════════════════════════════════════════
DEEP_PROFILE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

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

/* PII Risk Cards */
.pii-risk-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid;
    border-radius: 14px;
    padding: 1.2rem;
    transition: all 0.3s ease;
}
.pii-risk-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,.2);
}
.pii-risk-card.high {
    border-color: rgba(239,68,68,.5);
    background: linear-gradient(135deg, rgba(239,68,68,.15), rgba(239,68,68,.05));
}
.pii-risk-card.medium {
    border-color: rgba(251,191,36,.5);
    background: linear-gradient(135deg, rgba(251,191,36,.15), rgba(251,191,36,.05));
}
.pii-risk-card.low {
    border-color: rgba(16,185,129,.5);
    background: linear-gradient(135deg, rgba(16,185,129,.15), rgba(16,185,129,.05));
}

/* Validation Rule Cards */
.rule-card {
    background: linear-gradient(135deg, rgba(30,41,59,.8), rgba(15,23,42,.8));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
}
.rule-card:hover {
    border-color: rgba(99,102,241,.5);
    box-shadow: 0 4px 16px rgba(99,102,241,.12);
    transform: translateX(4px);
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


def adapt_pii_results(pii_results):
    """Adapt the features module PII results to the format expected by the tab UI"""
    pii_findings = {}
    
    for col_info in pii_results.get('pii_columns', []):
        col_name = col_info['column']
        pii_type = col_info['description']
        
        type_mapping = {
            'Email Address': 'Email',
            'US Phone Number': 'Phone',
            'Phone Number': 'Phone',
            'Social Security Number': 'SSN',
            'Credit Card Number': 'Credit Card',
            'IP Address': 'IP Address',
            'US ZIP Code': 'ZIP Code',
            'Person Name': 'Name',
            'Physical Address': 'Address',
            'Date of Birth': 'DOB',
            'Financial Information': 'Financial'
        }
        
        simplified_type = type_mapping.get(pii_type, pii_type)
        pii_findings[col_name] = simplified_type
    
    return pii_findings


def render_deep_profile_tab(df):
    """Render the Deep Profile tab with enhanced UI"""
    
    # Apply enhanced CSS
    st.markdown(DEEP_PROFILE_CSS, unsafe_allow_html=True)
    
    st.markdown('<h2 class="gradient-header">🔒 Deep Data Profile</h2>', unsafe_allow_html=True)
    st.caption("Detailed statistical analysis, custom rule validation, and PII detection - No AI required.")
    
    # ========================================================
    # DATA SOURCE SELECTOR
    # ========================================================
    data_sources = {"📄 Original Uploaded Data": df}
    
    if 'global_cleaned_df' in st.session_state and st.session_state.global_cleaned_df is not None:
        data_sources["✅ Cleaned Data (from Fix Data tab)"] = st.session_state.global_cleaned_df
    
    if 'skew_fixed_df' in st.session_state and st.session_state.skew_fixed_df is not None:
        data_sources["📐 Skewness-Corrected Data"] = st.session_state.skew_fixed_df
    
    if len(data_sources) > 1:
        st.info("💡 **Pro Tip:** Choose your cleaned/transformed data to mask PII without losing your data processing work!", icon="✨")
        
        source_col, info_col = st.columns([2, 1])
        
        with source_col:
            selected_source = st.selectbox(
                "📊 Select Data Source for PII Scan & Masking",
                options=list(data_sources.keys()),
                index=1 if len(data_sources) > 1 else 0,
                help="Choose the dataset version you want to scan and mask for PII"
            )
        
        with info_col:
            source_df = data_sources[selected_source]
            st.metric("Rows", len(source_df), delta=f"{len(source_df) - len(df):+}" if len(source_df) != len(df) else None)
            st.metric("Columns", len(source_df.columns), delta=f"{len(source_df.columns) - len(df.columns):+}" if len(source_df.columns) != len(df.columns) else None)
        
        working_df = source_df.copy()
        st.markdown("---")
    else:
        selected_source = list(data_sources.keys())[0]
        working_df = df.copy()
    
    # ========================================================
    # PII DETECTION SECTION WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🔐</span>
        <p class="title">PII (Personal Identifiable Information) Detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Scanning for PII..."):
        pii_results = detect_pii_features(working_df)
        pii_findings = adapt_pii_results(pii_results)
    
    if pii_findings:
        st.warning(f"⚠️ **{len(pii_findings)} potential PII column(s) detected!**", icon="⚠️")
        
        # Calculate Privacy Risk Score
        risk_score = 0
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for pii_type in pii_findings.values():
            if pii_type in ['SSN', 'Credit Card']:
                risk_score += 10
                high_risk_count += 1
            elif pii_type in ['Email', 'Phone', 'IP Address']:
                risk_score += 5
                medium_risk_count += 1
            else:
                risk_score += 2
                low_risk_count += 1
        
        col_risk, col_details = st.columns([1, 3])
        
        with col_risk:
            risk_color = "🔴" if risk_score >= 20 else "🟡" if risk_score >= 10 else "🟢"
            risk_label = "HIGH" if risk_score >= 20 else "MEDIUM" if risk_score >= 10 else "LOW"
            st.metric(
                "Privacy Risk Score", 
                f"{risk_score}/100 {risk_color}",
                delta=f"{risk_label} RISK",
                delta_color="inverse" if risk_score >= 20 else "off"
            )
        
        with col_details:
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            with detail_col1:
                st.metric("🔴 High Risk", high_risk_count, help="SSN, Credit Card")
            with detail_col2:
                st.metric("🟡 Medium Risk", medium_risk_count, help="Email, Phone, IP")
            with detail_col3:
                st.metric("🟢 Low Risk", low_risk_count, help="Name, Address, ZIP")
        
        st.markdown("---")
        
        pii_df = pd.DataFrame([
            {
                'Column': col, 
                'PII Type': pii_type, 
                'Risk': '🔴 High' if pii_type in ['SSN', 'Credit Card'] else '🟡 Medium' if pii_type in ['Email', 'Phone', 'IP Address'] else '🟢 Low',
                'Rows Affected': len(working_df)
            }
            for col, pii_type in pii_findings.items()
        ])
        
        st.dataframe(pii_df, hide_index=True, height=min(len(pii_df) * 35 + 38, 300))
        
        # Action Buttons
        st.markdown("#### 🛡️ Privacy Protection Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("🔒 Mask PII Data", type="primary", help="Replace PII with masked values"):
                masked_df = working_df.copy()
                mask_count = 0
                
                for col, pii_type in pii_findings.items():
                    if pii_type == 'Email':
                        masked_df[col] = masked_df[col].astype(str).str.replace(
                            r'^(.)[^@]*(@)(.)[^.]*(\..*)$', r'\1***\2***\4', regex=True
                        )
                        mask_count += 1
                    
                    elif pii_type == 'Phone':
                        def mask_phone(v):
                            if pd.isna(v): return v
                            s = str(v).strip()
                            if s in ['nan', 'None', '']: return v
                            d = ''.join(filter(str.isdigit, s))
                            return f'***-***-{d[-4:]}' if len(d) >= 4 else v
                        masked_df[col] = masked_df[col].apply(mask_phone)
                        mask_count += 1
                    
                    elif pii_type == 'SSN':
                        def mask_ssn(v):
                            if pd.isna(v): return v
                            s = str(v).strip().replace('-', '')
                            if s in ['nan', 'None', '']: return v
                            d = ''.join(filter(str.isdigit, s))
                            return f'***-**-{d[-4:]}' if len(d) >= 4 else v
                        masked_df[col] = masked_df[col].apply(mask_ssn)
                        mask_count += 1
                    
                    elif pii_type == 'Credit Card':
                        def mask_credit_card(v):
                            if pd.isna(v): return v
                            s = str(v).strip().replace(' ', '').replace('-', '')
                            if s in ['nan', 'None', '']: return v
                            d = ''.join(filter(str.isdigit, s))
                            return f'****-****-****-{d[-4:]}' if len(d) >= 4 else v
                        masked_df[col] = masked_df[col].apply(mask_credit_card)
                        mask_count += 1
                    
                    elif pii_type == 'IP Address':
                        def mask_ip(v):
                            if pd.isna(v): return v
                            s = str(v).strip()
                            if s in ['nan', 'None', '']: return v
                            parts = s.split('.')
                            return f'***.***.***.{parts[3]}' if len(parts) == 4 else s
                        masked_df[col] = masked_df[col].apply(mask_ip)
                        mask_count += 1
                    
                    elif pii_type == 'Name':
                        masked_df[col] = masked_df[col].astype(str).str.replace(
                            r'^(.).+$', r'\1***', regex=True
                        )
                        mask_count += 1
                
                st.session_state['masked_df'] = masked_df
                st.success(f"✅ Masked {mask_count} PII column(s)! Download below.")
                if len(data_sources) > 1:
                    st.info(f"📊 Based on: **{selected_source}**")
                st.rerun()
        
        with action_col2:
            if st.button("🗑️ Remove PII Columns", help="Drop all PII columns from dataset"):
                pii_clean_df = working_df.drop(columns=list(pii_findings.keys()))
                st.session_state['pii_clean_df'] = pii_clean_df
                st.success(f"✅ Removed {len(pii_findings)} PII column(s)! Download below.")
                if len(data_sources) > 1:
                    st.info(f"📊 Based on: **{selected_source}**")
                st.rerun()
        
        with action_col3:
            if st.button("📋 View Recommendations"):
                st.session_state['show_pii_recs'] = True
                st.rerun()
        
        st.markdown("---")
        fmt = get_format_label()
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            if 'masked_df' in st.session_state:
                smart_download_button(
                    df=st.session_state['masked_df'],
                    label=f"📥 Download Masked Data ({fmt})",
                    suffix="pii_masked",
                    key="dl_pii_masked",
                    button_width=None,
                    help_text="Download dataset with PII masked"
                )
        
        with download_col2:
            if 'pii_clean_df' in st.session_state:
                smart_download_button(
                    df=st.session_state['pii_clean_df'],
                    label=f"📥 Download Without PII ({fmt})",
                    suffix="no_pii",
                    key="dl_no_pii",
                    button_width=None,
                    help_text="Download dataset with PII columns removed"
                )
        
        # PII recommendations
        if st.session_state.get('show_pii_recs', False):
            with st.expander("🛡️ PII Protection Recommendations", expanded=True):
                st.markdown("""
                **Recommended Actions:**
                
                1. **🔒 Anonymize/Hash**: Replace actual values with hashed versions
                2. **🗑️ Remove**: Drop PII columns if not needed for analysis
                3. **🔐 Encrypt**: Use encryption for sensitive data storage
                4. **⚠️ Access Control**: Restrict who can view this data
                5. **📝 Compliance**: Ensure GDPR/CCPA/HIPAA compliance if applicable
                
                **Detailed Recommendations per Column:**
                """)
                
                for col, pii_type in pii_findings.items():
                    if pii_type == 'Email':
                        st.markdown(f"- **{col}** ({pii_type}): Consider masking (e.g., `u***@example.com`) ✅ Available above")
                    elif pii_type == 'Phone':
                        st.markdown(f"- **{col}** ({pii_type}): Consider masking (e.g., `***-***-1234`) ✅ Available above")
                    elif pii_type == 'SSN':
                        st.markdown(f"- **{col}** ({pii_type}): 🔴 **HIGH RISK** - Should be encrypted or removed ✅ Available above")
                    elif pii_type == 'Credit Card':
                        st.markdown(f"- **{col}** ({pii_type}): 🔴 **HIGH RISK** - Must be encrypted (PCI-DSS) ✅ Available above")
                    elif pii_type == 'Name':
                        st.markdown(f"- **{col}** ({pii_type}): Consider pseudonymization ✅ Available above")
                    elif pii_type == 'Address':
                        st.markdown(f"- **{col}** ({pii_type}): Consider generalization (e.g., zip code only)")
                    elif pii_type == 'IP Address':
                        st.markdown(f"- **{col}** ({pii_type}): Consider anonymizing IP addresses ✅ Available above")
                    else:
                        st.markdown(f"- **{col}** ({pii_type}): Review and protect as needed")
                
                st.markdown("---")
                st.info("💡 **Tip**: Use the action buttons above to quickly mask or remove PII from your dataset!")
        else:
            with st.expander("🛡️ PII Protection Recommendations", expanded=False):
                st.markdown("""
                **Recommended Actions:**
                
                1. **🔒 Anonymize/Hash**: Replace actual values with hashed versions
                2. **🗑️ Remove**: Drop PII columns if not needed for analysis
                3. **🔐 Encrypt**: Use encryption for sensitive data storage
                4. **⚠️ Access Control**: Restrict who can view this data
                5. **📝 Compliance**: Ensure GDPR/CCPA/HIPAA compliance if applicable
                
                Click "📋 View Recommendations" above for detailed advice on each column.
                """)
    else:
        st.success("✅ No obvious PII detected in column names or content patterns", icon="✅")
        st.caption("Note: This is a basic scan. Always review your data for context-specific sensitive information.")
    
    st.markdown("---")
    
    # ========================================================
    # CUSTOM VALIDATION RULES WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🎯</span>
        <p class="title">Custom Validation Rules</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Create & Run Validation Rules", expanded=True):
        if 'validation_rules' not in st.session_state:
            st.session_state.validation_rules = []
        
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            rule_col = st.selectbox("Column", df.columns)
        
        with c2:
            if pd.api.types.is_numeric_dtype(df[rule_col]):
                rule_type = st.selectbox("Condition", ["Positive (>0)", "Non-Negative (>=0)", "No Nulls"])
            else:
                rule_type = st.selectbox("Condition", ["No Nulls", "Unique Values Only"])
        
        with c3:
            if st.button("➕ Add Rule"):
                st.session_state.validation_rules.append({'col': rule_col, 'type': rule_type})
                st.rerun()
        
        if st.session_state.validation_rules:
            st.markdown("**Active Rules:**")
            for i, rule in enumerate(st.session_state.validation_rules):
                cols = st.columns([4, 1])
                cols[0].info(f"{rule['col']} -> {rule['type']}")
                if cols[1].button("🗑️", key=f"del_{i}"):
                    st.session_state.validation_rules.pop(i)
                    st.rerun()
            
            if st.button("▶️ Run Validation Check", type="primary"):
                errors = []
                for rule in st.session_state.validation_rules:
                    c = rule['col']
                    t = rule['type']
                    
                    if t == "No Nulls":
                        fail = df[c].isna().sum()
                        if fail > 0:
                            errors.append(f"❌ {c}: Found {fail} nulls")
                    elif t == "Unique Values Only":
                        fail = df.duplicated(subset=[c]).sum()
                        if fail > 0:
                            errors.append(f"❌ {c}: Found {fail} duplicates")
                    elif t == "Positive (>0)":
                        fail = (df[c] <= 0).sum()
                        if fail > 0:
                            errors.append(f"❌ {c}: Found {fail} values <= 0")
                    elif t == "Non-Negative (>=0)":
                        fail = (df[c] < 0).sum()
                        if fail > 0:
                            errors.append(f"❌ {c}: Found {fail} negative values")
                
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    st.success("✅ All validation rules passed!")
    
    st.markdown("---")
    
    # ========================================================
    # DETAILED COLUMN PROFILING WITH ENHANCED UI
    # ========================================================
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">📊</span>
        <p class="title">Column-by-Column Report</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("⚠️ **Note:** This analysis uses the **ORIGINAL uploaded data** (not cleaned versions from Fix Data tab)")
    
    selected_profile_col = st.selectbox("Select column to inspect:", df.columns)
    
    col_data = df[selected_profile_col]
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Type", str(col_data.dtype))
        st.metric("Missing", f"{col_data.isna().sum()} ({col_data.isna().mean():.1%})")
    
    with c2:
        st.metric("Unique Values", col_data.nunique())
        st.metric("Memory Usage", f"{col_data.memory_usage() / 1024:.1f} KB")
    
    with c3:
        if pd.api.types.is_numeric_dtype(col_data):
            st.metric("Mean", f"{col_data.mean():.2f}")
            st.metric("Median", f"{col_data.median():.2f}")
        else:
            top_val = col_data.mode()[0] if not col_data.mode().empty else "N/A"
            st.metric("Most Frequent", str(top_val))
    
    if pd.api.types.is_numeric_dtype(col_data):
        fig = px.histogram(
            col_data, x=selected_profile_col,
            title=f"Distribution of {selected_profile_col}",
            color_discrete_sequence=['#8b5cf6']
        )
        fig.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig)
    else:
        top_counts = col_data.value_counts().head(10)
        fig = px.bar(
            x=top_counts.values, y=top_counts.index, orientation='h',
            title=f"Top 10 Values in {selected_profile_col}",
            color_discrete_sequence=['#8b5cf6']
        )
        fig.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig)