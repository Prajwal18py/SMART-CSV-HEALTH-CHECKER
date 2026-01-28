"""
Tab 9: Compare Datasets
Data drift detection and schema comparison
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_compare_tab(df):
    """Render the Compare Datasets tab"""
    
    st.markdown('<h2 class="gradient-header">📈 Compare Datasets</h2>', unsafe_allow_html=True)
    st.caption("Upload a second CSV file to detect data drift and schema changes.")
    
    compare_file = st.file_uploader("Upload Comparison CSV", type=['csv'], key="compare_csv_tab")
    
    if compare_file:
        try:
            df_compare = pd.read_csv(compare_file)
            
            st.markdown("---")
            
            # Basic stats comparison
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Original Rows", f"{len(df):,}")
                st.metric("Compare Rows", f"{len(df_compare):,}", delta=f"{len(df_compare) - len(df):+,}")
            
            with col2:
                st.metric("Original Cols", len(df.columns))
                st.metric("Compare Cols", len(df_compare.columns), delta=f"{len(df_compare.columns) - len(df.columns):+}")
            
            with col3:
                orig_missing = df.isna().sum().sum()
                comp_missing = df_compare.isna().sum().sum()
                st.metric("Original Missing", f"{orig_missing:,}")
                st.metric("Compare Missing", f"{comp_missing:,}", delta=f"{comp_missing - orig_missing:+,}")
            
            st.markdown("---")
            
            # Schema comparison
            st.subheader("🗂️ Schema Changes")
            missing_cols = set(df.columns) - set(df_compare.columns)
            new_cols = set(df_compare.columns) - set(df.columns)
            
            if missing_cols or new_cols:
                col_schema1, col_schema2 = st.columns(2)
                
                with col_schema1:
                    if missing_cols:
                        st.error(f"**Removed Columns ({len(missing_cols)}):**")
                        for col in list(missing_cols)[:10]:
                            st.markdown(f"- ❌ {col}")
                
                with col_schema2:
                    if new_cols:
                        st.success(f"**New Columns ({len(new_cols)}):**")
                        for col in list(new_cols)[:10]:
                            st.markdown(f"- ✅ {col}")
            else:
                st.success("✅ No schema changes detected")
            
            # Statistical drift
            st.markdown("---")
            st.subheader("📊 Statistical Drift")
            
            common_cols = set(df.columns) & set(df_compare.columns)
            numeric_common = [
                c for c in common_cols
                if pd.api.types.is_numeric_dtype(df[c]) and pd.api.types.is_numeric_dtype(df_compare[c])
            ]
            
            drift_data = []
            for col in numeric_common[:10]:
                orig_mean = df[col].mean()
                comp_mean = df_compare[col].mean()
                
                if orig_mean != 0:
                    pct_change = ((comp_mean - orig_mean) / orig_mean) * 100
                    
                    if abs(pct_change) > 10:
                        drift_data.append({
                            'Column': col,
                            'Original Mean': f"{orig_mean:.2f}",
                            'New Mean': f"{comp_mean:.2f}",
                            'Change %': f"{pct_change:+.1f}%",
                            'Status': '⚠️ Drift' if abs(pct_change) > 20 else '📊 Change'
                        })
            
            if drift_data:
                st.warning(f"**Detected drift in {len(drift_data)} columns:**")
                st.dataframe(pd.DataFrame(drift_data), use_container_width=True)
            else:
                st.success("✅ No significant statistical drift detected")
            
            # Distribution comparison
            if numeric_common:
                st.markdown("---")
                st.subheader("📉 Distribution Comparison")
                
                compare_col = st.selectbox("Select column to visualize:", numeric_common, key="drift_col_select")
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=df[compare_col], name='Original',
                    opacity=0.7, marker_color='#6366f1'
                ))
                fig.add_trace(go.Histogram(
                    x=df_compare[compare_col], name='Compare',
                    opacity=0.7, marker_color='#10b981'
                ))
                
                fig.update_layout(
                    barmode='overlay',
                    title=f"Distribution Comparison: {compare_col}",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error comparing files: {e}")
    else:
        st.info("👆 Upload a file above to start comparison")