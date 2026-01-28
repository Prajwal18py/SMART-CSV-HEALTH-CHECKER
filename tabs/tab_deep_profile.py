"""
Tab 8:  Deep Profile
Custom validation rules and detailed column profiling
"""
import streamlit as st
import pandas as pd
import plotly.express as px


def render_deep_profile_tab(df):
    """Render the Deep Profile tab"""
    
    st.markdown('<h2 class="gradient-header">🔒 Deep Data Profile</h2>', unsafe_allow_html=True)
    st.caption("Detailed statistical analysis and custom rule validation - No AI required.")
    
    # Custom Rule Builder
    with st.expander("🎯 Create Validation Rules", expanded=True):
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
        
        # Show active rules
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
    
    # Detailed Column Profiling
    st.markdown("### 📊 Column-by-Column Report")
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
    
    # Mini Visualization
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
        st.plotly_chart(fig, use_container_width=True)
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
        st.plotly_chart(fig, use_container_width=True)