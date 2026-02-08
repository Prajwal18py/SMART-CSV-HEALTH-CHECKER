"""
Tab: Skewness Analysis & Correction
Detect and fix highly skewed features with advanced transformations
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

def render_skewness_tab(df, sidebar_settings=None):
    """
    Render the Enhanced Skewness Analysis & Correction Tab
    
    Args:
        df: DataFrame to analyze
        sidebar_settings: Optional settings from sidebar (not currently used but kept for consistency)
    """
    st.subheader("📐 Skewness Analysis & Correction")
    
    # ========================================================
    # ✨ DATA SOURCE SELECTOR - Use Cleaned Data if Available
    # ========================================================
    cleaned_data_available = False
    data_sources = {"📄 Original Uploaded Data": df}
    
    # Check for cleaned data from Fix Data tab
    if 'global_cleaned_df' in st.session_state and st.session_state.global_cleaned_df is not None:
        data_sources["✅ Cleaned Data (from Fix Data tab)"] = st.session_state.global_cleaned_df
        cleaned_data_available = True
    
    # Show data source selector if cleaned data exists
    if cleaned_data_available:
        st.info("💡 **Pro Tip:** Cleaned data from the Fix Data tab is available! Use it for better skewness analysis.", icon="✨")
        
        col_selector, col_info = st.columns([2, 1])
        
        with col_selector:
            selected_source = st.selectbox(
                "📊 Choose Data Source",
                options=list(data_sources.keys()),
                index=1,  # Default to cleaned data
                help="Use cleaned data for more accurate skewness analysis"
            )
        
        with col_info:
            if selected_source == "✅ Cleaned Data (from Fix Data tab)":
                st.metric("Missing Values", "0", delta="✅ Clean", delta_color="off")
            else:
                missing_count = df.isna().sum().sum()
                st.metric("Missing Values", missing_count, delta="⚠️ Has nulls", delta_color="inverse")
        
        # Use selected data source
        working_df = data_sources[selected_source].copy()
        
        st.markdown("---")
    else:
        # No cleaned data available - inform user
        missing_count = df.isna().sum().sum()
        
        if missing_count > 0:
            st.warning(
                f"⚠️ **{missing_count} missing values detected.** "
                "For better results, clean your data first in the **Fix Data** tab, "
                "then return here to use the cleaned version!",
                icon="💡"
            )
        
        # Use original data
        working_df = df.copy()
    
    # Initialize session state for tracking transformations
    if 'transformations_log' not in st.session_state:
        st.session_state['transformations_log'] = []
    if 'original_df_backup' not in st.session_state:
        st.session_state['original_df_backup'] = working_df.copy()
    
    # ========================================================
    # 1. IDENTIFY SKEWED COLUMNS
    # ========================================================
    numeric_cols = working_df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) == 0:
        st.warning("⚠️ No numeric columns found in the dataset.")
        return
    
    # Calculate skewness for all numeric columns
    skew_vals = working_df[numeric_cols].apply(lambda x: x.dropna().skew()).sort_values(ascending=False)
    
    # Filter for high skewness (absolute value > 1.0 is standard threshold)
    high_skew = skew_vals[abs(skew_vals) > 1.0]
    moderate_skew = skew_vals[(abs(skew_vals) > 0.5) & (abs(skew_vals) <= 1.0)]
    
    if high_skew.empty and moderate_skew.empty:
        st.success("✅ No skewed columns detected! Your data distribution looks excellent.", icon="✅")
        return

    # ========================================================
    # 2. OVERVIEW METRICS WITH VISUAL DASHBOARD
    # ========================================================
    st.markdown("### 📊 Skewness Overview")
    
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("📈 Highly Skewed", len(high_skew), 
                 help="Absolute skewness > 1.0")
    with metric_cols[1]:
        st.metric("📊 Moderately Skewed", len(moderate_skew),
                 help="Absolute skewness 0.5-1.0")
    with metric_cols[2]:
        st.metric("✅ Normal", len(skew_vals) - len(high_skew) - len(moderate_skew),
                 help="Absolute skewness < 0.5")
    with metric_cols[3]:
        st.metric("🔧 Transformations Applied", len(st.session_state['transformations_log']))
    
    # Skewness Distribution Chart
    with st.expander("📈 View All Skewness Values", expanded=False):
        col_chart, col_table = st.columns([2, 1])
        
        with col_chart:
            # Create color-coded bar chart
            colors = ['#FF4B4B' if abs(val) > 1.0 else '#FFA15A' if abs(val) > 0.5 else '#00CC96' 
                     for val in skew_vals.values]
            
            fig_overview = go.Figure(data=[
                go.Bar(x=skew_vals.index, y=skew_vals.values, marker_color=colors)
            ])
            fig_overview.add_hline(y=1.0, line_dash="dash", line_color="red", 
                                  annotation_text="High Threshold (+1.0)")
            fig_overview.add_hline(y=-1.0, line_dash="dash", line_color="red",
                                  annotation_text="High Threshold (-1.0)")
            fig_overview.add_hline(y=0.5, line_dash="dot", line_color="orange")
            fig_overview.add_hline(y=-0.5, line_dash="dot", line_color="orange")
            fig_overview.update_layout(
                title="Skewness Distribution Across Features",
                xaxis_title="Features",
                yaxis_title="Skewness Value",
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_overview)
        
        with col_table:
            skew_df = pd.DataFrame({
                'Feature': skew_vals.index,
                'Skewness': skew_vals.values,
                'Severity': ['High' if abs(val) > 1.0 else 'Moderate' if abs(val) > 0.5 else 'Normal' 
                           for val in skew_vals.values]
            })
            st.dataframe(skew_df, height=300)

    if high_skew.empty:
        st.info("💡 Only moderate skewness detected. You may still apply transformations if needed.")
        skew_to_fix = moderate_skew
    else:
        skew_to_fix = high_skew

    st.markdown("---")

    # ========================================================
    # 3. TRANSFORMATION MODE SELECTOR
    # ========================================================
    st.markdown("### 🛠️ Transformation Tools")
    
    mode_tab1, mode_tab2, mode_tab3 = st.tabs(["🎯 Single Column", "⚡ Bulk Transform", "📋 Manage Transformations"])
    
    # ========================================================
    # TAB 1: SINGLE COLUMN TRANSFORMATION
    # ========================================================
    with mode_tab1:
        col_sel, col_act = st.columns([1, 2])
        
        with col_sel:
            selected_col = st.selectbox(
                "Select Column to Transform",
                skew_to_fix.index.tolist(),
                key="single_col_select"
            )
            
            st.markdown("##### Transformation Method")
            method = st.radio(
                "Choose method:",
                [
                    "Log (np.log1p)",
                    "Square Root (np.sqrt)",
                    "Cube Root (np.cbrt)",
                    "Box-Cox (Auto)",
                    "Yeo-Johnson (Auto)",
                    "Reciprocal (1/x)"
                ],
                help="""
                **Log:** Best for strong positive skew  
                **Square Root:** Mild positive skew  
                **Cube Root:** Works with negative values  
                **Box-Cox:** Auto-finds optimal (positive only)  
                **Yeo-Johnson:** Auto-finds optimal (any values)  
                **Reciprocal:** Strong right skew
                """,
                key="transformation_method"
            )
            
            show_qq = st.checkbox("Show Q-Q Plot", value=False, 
                                 help="Visualize how close the data is to normal distribution")
            
            show_stats = st.checkbox("Show Detailed Statistics", value=True)
        
        # ========================================================
        # 4. CALCULATE TRANSFORMATIONS
        # ========================================================
        with col_act:
            if selected_col:
                # Get original data
                original_data = working_df[selected_col].dropna()
                original_skew = original_data.skew()
                
                # Auto-recommend best transformation
                st.markdown("#### 💡 Auto-Recommendation")
                best_transform, best_skew = _find_best_transformation(original_data)
                
                recommendation_color = "green" if best_transform.lower() in method.lower() else "blue"
                st.markdown(f":{recommendation_color}[**Recommended:** {best_transform} (skewness: {best_skew:.3f})]")
                
                # Apply selected transformation
                transformed_data, shift, error_msg = _apply_transformation(original_data, method)
                
                if error_msg:
                    st.error(f"❌ {error_msg}")
                else:
                    new_skew = pd.Series(transformed_data).skew()
                    
                    # ========================================================
                    # 5. VISUALIZATION: HISTOGRAMS
                    # ========================================================
                    st.markdown("#### 📊 Distribution Comparison")
                    
                    hist_col1, hist_col2 = st.columns(2)
                    
                    with hist_col1:
                        st.caption(f"**Original Distribution** (Skew: `{original_skew:.3f}`)")
                        fig1 = go.Figure(data=[
                            go.Histogram(x=original_data, 
                                       marker_color='#FF4B4B', 
                                       opacity=0.75,
                                       name="Original",
                                       nbinsx=30)
                        ])
                        fig1.add_vline(x=original_data.mean(), 
                                      line_dash="dash", 
                                      line_color="white",
                                      annotation_text="Mean")
                        fig1.update_layout(
                            margin=dict(l=10, r=10, t=30, b=10),
                            height=250,
                            showlegend=False,
                            xaxis_title=selected_col,
                            yaxis_title="Frequency"
                        )
                        st.plotly_chart(fig1)
                    
                    with hist_col2:
                        is_improved = abs(new_skew) < abs(original_skew)
                        color = '#00CC96' if is_improved else '#FFA15A'
                        improvement_emoji = "✅" if is_improved else "⚠️"
                        
                        st.caption(f"**Transformed Distribution** (Skew: `{new_skew:.3f}`) {improvement_emoji}")
                        fig2 = go.Figure(data=[
                            go.Histogram(x=transformed_data,
                                       marker_color=color,
                                       opacity=0.75,
                                       name="Transformed",
                                       nbinsx=30)
                        ])
                        fig2.add_vline(x=np.mean(transformed_data),
                                      line_dash="dash",
                                      line_color="white",
                                      annotation_text="Mean")
                        fig2.update_layout(
                            margin=dict(l=10, r=10, t=30, b=10),
                            height=250,
                            showlegend=False,
                            xaxis_title=f"Transformed {selected_col}",
                            yaxis_title="Frequency"
                        )
                        st.plotly_chart(fig2)
                    
                    # ========================================================
                    # 6. Q-Q PLOT (OPTIONAL)
                    # ========================================================
                    if show_qq:
                        st.markdown("#### 📈 Q-Q Plot (Normality Check)")
                        qq_col1, qq_col2 = st.columns(2)
                        
                        with qq_col1:
                            fig_qq1 = _create_qq_plot(original_data, "Original")
                            st.plotly_chart(fig_qq1)
                        
                        with qq_col2:
                            fig_qq2 = _create_qq_plot(transformed_data, "Transformed")
                            st.plotly_chart(fig_qq2)
                    
                    # ========================================================
                    # 7. DETAILED STATISTICS (OPTIONAL)
                    # ========================================================
                    if show_stats:
                        st.markdown("#### 📋 Statistical Summary")
                        stats_col1, stats_col2 = st.columns(2)
                        
                        with stats_col1:
                            st.markdown("**Original**")
                            _display_statistics(original_data)
                        
                        with stats_col2:
                            st.markdown("**Transformed**")
                            _display_statistics(pd.Series(transformed_data))
                    
                    # ========================================================
                    # 8. APPLY BUTTON
                    # ========================================================
                    st.markdown("---")
                    apply_col1, apply_col2, apply_col3 = st.columns([1, 1, 1])
                    
                    with apply_col1:
                        if st.button(f"✨ Apply Transformation", type="primary", width="stretch"):
                            # ✅ FIX: Create full-length series with NaNs preserved
                            full_transformed = pd.Series(index=working_df.index, dtype=float)
                            full_transformed.loc[working_df[selected_col].notna()] = transformed_data
                            
                            # Store transformation log
                            st.session_state['transformations_log'].append({
                                'column': selected_col,
                                'method': method,
                                'shift': shift,
                                'original_skew': original_skew,
                                'new_skew': new_skew,
                                'timestamp': pd.Timestamp.now()
                            })
                            
                            # Apply to dataframe
                            working_df[selected_col] = full_transformed
                            st.session_state['skew_fixed_df'] = working_df
                            
                            if shift > 0:
                                st.toast(f"ℹ️ Data shifted by {shift:.2f} to handle negative/zero values", icon="ℹ️")
                            
                            improvement_pct = ((abs(original_skew) - abs(new_skew)) / abs(original_skew) * 100) if original_skew != 0 else 0
                            st.toast(f"✅ Transform applied! Skewness improved by {improvement_pct:.1f}%", icon="✅")
                            st.rerun()
                    
                    with apply_col2:
                        if is_improved:
                            improvement_pct = ((abs(original_skew) - abs(new_skew)) / abs(original_skew) * 100)
                            st.success(f"📈 {improvement_pct:.1f}% improvement")
                        else:
                            st.warning("⚠️ No improvement")
                    
                    with apply_col3:
                        # Quick download button (only if transformations exist)
                        if 'skew_fixed_df' in st.session_state and len(st.session_state.get('transformations_log', [])) > 0:
                            transformed_df = st.session_state['skew_fixed_df']
                            csv_data = transformed_df.to_csv(index=False)
                            st.download_button(
                                "⬇️ Quick Download",
                                data=csv_data,
                                file_name="data_transformed.csv",
                                mime="text/csv",
                                width="stretch",
                                help="Download transformed dataset"
                            )
                        elif shift > 0:
                            st.info(f"ℹ️ Shift: +{shift:.2f}")
    
    # ========================================================
    # TAB 2: BULK TRANSFORMATION
    # ========================================================
    with mode_tab2:
        st.markdown("Apply the same transformation to multiple columns at once.")
        
        bulk_col1, bulk_col2 = st.columns([1, 1])
        
        with bulk_col1:
            bulk_columns = st.multiselect(
                "Select Columns for Bulk Transform",
                skew_to_fix.index.tolist(),
                default=skew_to_fix.index.tolist()[:min(3, len(skew_to_fix))],
                key="bulk_select"
            )
            
            bulk_method = st.selectbox(
                "Transformation Method",
                [
                    "Auto (Best for Each)",
                    "Log (np.log1p)",
                    "Square Root (np.sqrt)",
                    "Yeo-Johnson (Auto)"
                ],
                key="bulk_method"
            )
            
            if st.button("⚡ Apply to All Selected", type="primary", width="stretch"):
                if bulk_columns:
                    # ✨ Professional loading UI
                    with st.status(f"🔄 Transforming {len(bulk_columns)} columns...", expanded=True) as status:
                        results = []
                        progress = st.progress(0)
                        
                        for idx, col in enumerate(bulk_columns):
                            st.write(f"✨ Processing: **{col}**")
                            
                            original_data = working_df[col].dropna()
                            original_skew = original_data.skew()
                            
                            if bulk_method == "Auto (Best for Each)":
                                best_method, _ = _find_best_transformation(original_data)
                                transformed_data, shift, _ = _apply_transformation(original_data, best_method)
                                method_used = best_method
                            else:
                                transformed_data, shift, _ = _apply_transformation(original_data, bulk_method)
                                method_used = bulk_method
                            
                            new_skew = pd.Series(transformed_data).skew()
                            
                            # ✅ FIX: Create full-length series with NaNs preserved
                            full_transformed = pd.Series(index=working_df.index, dtype=float)
                            full_transformed.loc[working_df[col].notna()] = transformed_data
                            
                            # Apply transformation
                            working_df[col] = full_transformed
                            
                            # Log transformation
                            st.session_state['transformations_log'].append({
                                'column': col,
                                'method': method_used,
                                'shift': shift,
                                'original_skew': original_skew,
                                'new_skew': new_skew,
                                'timestamp': pd.Timestamp.now()
                            })
                            
                            results.append({
                                'Column': col,
                                'Method': method_used,
                                'Original Skew': f"{original_skew:.3f}",
                                'New Skew': f"{new_skew:.3f}",
                                'Improvement': f"{((abs(original_skew) - abs(new_skew)) / abs(original_skew) * 100):.1f}%" if original_skew != 0 else "N/A"
                            })
                            
                            # Update progress
                            progress.progress((idx + 1) / len(bulk_columns))
                        
                        # Clear progress bar
                        progress.empty()
                        
                        # Update status to complete
                        status.update(label="✅ Transformation Complete!", state="complete", expanded=False)
                        
                        st.session_state['skew_fixed_df'] = working_df
                        st.success(f"✅ Successfully transformed {len(bulk_columns)} columns!")
                        
                        # Show results
                        with bulk_col2:
                            st.markdown("#### Transformation Results")
                            st.dataframe(pd.DataFrame(results), hide_index=True)
                        
                        # Quick download after bulk transform
                        st.markdown("---")
                        quick_dl_col1, quick_dl_col2 = st.columns([2, 1])
                        
                        with quick_dl_col1:
                            st.success(f"🎉 {len(bulk_columns)} columns transformed successfully!")
                        
                        with quick_dl_col2:
                            csv_data = working_df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Transformed Data",
                                data=csv_data,
                                file_name="data_bulk_transformed.csv",
                                mime="text/csv",
                                type="primary",
                                width="stretch"
                            )
                        
                        st.rerun()
        
        with bulk_col2:
            if bulk_columns:
                st.markdown("#### Preview: Selected Columns")
                preview_df = pd.DataFrame({
                    'Column': bulk_columns,
                    'Current Skew': [f"{working_df[col].dropna().skew():.3f}" for col in bulk_columns],
                    'Severity': ['High' if abs(working_df[col].dropna().skew()) > 1.0 else 'Moderate' 
                               for col in bulk_columns]
                })
                st.dataframe(preview_df, hide_index=True)
    
    # ========================================================
    # TAB 3: MANAGE TRANSFORMATIONS
    # ========================================================
    with mode_tab3:
        # Quick Download at the top (always visible if transformations exist)
        if 'skew_fixed_df' in st.session_state and len(st.session_state.get('transformations_log', [])) > 0:
            quick_col1, quick_col2 = st.columns([3, 1])
            
            with quick_col1:
                st.info(f"📊 **{len(st.session_state['transformations_log'])}** transformations active on your dataset")
            
            with quick_col2:
                csv_data = st.session_state['skew_fixed_df'].to_csv(index=False)
                st.download_button(
                    "📥 Download Data",
                    data=csv_data,
                    file_name="data_transformed.csv",
                    mime="text/csv",
                    type="primary",
                    width="stretch"
                )
            
            st.markdown("---")
        
        if len(st.session_state['transformations_log']) == 0:
            st.info("📝 No transformations applied yet. Use the tabs above to transform columns.")
        else:
            st.markdown("#### 📜 Transformation History")
            
            log_df = pd.DataFrame(st.session_state['transformations_log'])
            log_df['Improvement %'] = ((abs(log_df['original_skew']) - abs(log_df['new_skew'])) / 
                                       abs(log_df['original_skew']) * 100).round(1)
            
            display_cols = ['column', 'method', 'original_skew', 'new_skew', 'Improvement %', 'timestamp']
            log_df_display = log_df[display_cols].copy()
            log_df_display.columns = ['Column', 'Method', 'Original Skew', 'New Skew', 'Improvement %', 'Timestamp']
            
            st.dataframe(log_df_display, hide_index=True)
            
            # Action buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                # Download transformation recipe
                csv_data = log_df_display.to_csv(index=False)
                st.download_button(
                    "📥 Download Recipe (CSV)",
                    data=csv_data,
                    file_name="transformation_recipe.csv",
                    mime="text/csv",
                    width="stretch"
                )
            
            with btn_col2:
                # Reset all transformations
                if st.button("↩️ Reset All Transformations", width="stretch"):
                    working_df = st.session_state['original_df_backup'].copy()
                    st.session_state['skew_fixed_df'] = working_df
                    st.session_state['transformations_log'] = []
                    st.success("✅ All transformations have been reset!")
                    st.rerun()
            
            with btn_col3:
                # Clear history (keep transformations)
                if st.button("🗑️ Clear History Log", width="stretch"):
                    st.session_state['transformations_log'] = []
                    st.rerun()
            
            # Summary statistics
            st.markdown("#### 📊 Summary")
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.metric("Total Transformations", len(log_df))
            
            with summary_col2:
                avg_improvement = log_df['Improvement %'].mean()
                st.metric("Avg Improvement", f"{avg_improvement:.1f}%")
            
            with summary_col3:
                most_used = log_df['method'].mode()[0] if len(log_df) > 0 else "N/A"
                st.metric("Most Used Method", most_used)
    
    # ========================================================
    # DOWNLOAD TRANSFORMED DATA (Always visible if transformations exist)
    # ========================================================
    st.markdown("---")
    
    if 'skew_fixed_df' in st.session_state and len(st.session_state.get('transformations_log', [])) > 0:
        st.markdown("### 📥 Export Transformed Data")
        
        transformed_df = st.session_state['skew_fixed_df']
        transformed_cols = list(set([t['column'] for t in st.session_state['transformations_log']]))
        
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            # Show quick stats
            st.markdown("##### ✅ Transformation Summary")
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            with summary_col1:
                st.metric("Columns Transformed", len(transformed_cols))
            
            with summary_col2:
                st.metric("Total Transformations", len(st.session_state['transformations_log']))
            
            with summary_col3:
                avg_improvement = sum([
                    ((abs(t['original_skew']) - abs(t['new_skew'])) / abs(t['original_skew']) * 100) 
                    if t['original_skew'] != 0 else 0
                    for t in st.session_state['transformations_log']
                ]) / len(st.session_state['transformations_log'])
                st.metric("Avg Improvement", f"{avg_improvement:.1f}%")
            
            st.caption(f"**Transformed columns:** {', '.join(transformed_cols)}")
        
        with col_right:
            st.write("")
            st.write("")
            # Download button
            csv_data = transformed_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name="data_skewness_corrected.csv",
                mime="text/csv",
                type="primary",
                width="stretch",
                help="Download your dataset with all skewness transformations applied"
            )
        
        # Optional: Show preview of transformed data
        with st.expander("👁️ Preview Transformed Data", expanded=False):
            st.dataframe(transformed_df.head(100), height=300)
    
    else:
        st.info("💡 Apply transformations above to download the corrected dataset")


# ========================================================
# HELPER FUNCTIONS
# ========================================================

def _apply_transformation(data, method):
    """
    Apply the selected transformation to the data.
    Returns: (transformed_data, shift_amount, error_message)
    """
    transformed_data = data.copy()
    shift = 0
    error_msg = None
    
    try:
        if "Log" in method:
            if (data <= 0).any():
                shift = abs(data.min()) + 1
                transformed_data = np.log1p(data + shift)
            else:
                transformed_data = np.log1p(data)
        
        elif "Square Root" in method:
            if (data < 0).any():
                shift = abs(data.min())
                transformed_data = np.sqrt(data + shift)
            else:
                transformed_data = np.sqrt(data)
        
        elif "Cube Root" in method:
            # Cube root works with negative values
            transformed_data = np.cbrt(data)
        
        elif "Box-Cox" in method:
            if (data <= 0).any():
                shift = abs(data.min()) + 1
                transformed_data, _ = stats.boxcox(data + shift)
            else:
                transformed_data, _ = stats.boxcox(data)
        
        elif "Yeo-Johnson" in method:
            # Yeo-Johnson works with any values
            transformed_data, _ = stats.yeojohnson(data)
        
        elif "Reciprocal" in method:
            if (data == 0).any():
                error_msg = "Reciprocal transformation cannot be applied to data containing zeros."
                return data, 0, error_msg
            transformed_data = 1 / data
    
    except Exception as e:
        error_msg = f"Transformation failed: {str(e)}"
        return data, 0, error_msg
    
    return transformed_data, shift, error_msg


def _find_best_transformation(data):
    """
    Test multiple transformations and return the one that minimizes skewness.
    Returns: (best_method_name, best_skewness_value)
    """
    methods = [
        "Log (np.log1p)",
        "Square Root (np.sqrt)",
        "Cube Root (np.cbrt)",
        "Yeo-Johnson (Auto)"
    ]
    
    results = {}
    
    for method in methods:
        transformed, _, error = _apply_transformation(data, method)
        if error is None:
            skewness = abs(pd.Series(transformed).skew())
            results[method] = skewness
    
    if not results:
        return "No transformation", data.skew()
    
    best_method = min(results, key=results.get)
    return best_method, results[best_method]


def _create_qq_plot(data, title):
    """
    Create a Q-Q plot to assess normality.
    """
    qq_data = stats.probplot(data, dist="norm")
    
    fig = go.Figure()
    
    # Scatter plot of theoretical vs sample quantiles
    fig.add_trace(go.Scatter(
        x=qq_data[0][0],
        y=qq_data[0][1],
        mode='markers',
        name='Data',
        marker=dict(color='#636EFA', size=6)
    ))
    
    # Reference line
    fig.add_trace(go.Scatter(
        x=qq_data[0][0],
        y=qq_data[1][0] * qq_data[0][0] + qq_data[1][1],
        mode='lines',
        name='Normal Distribution',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title=f"Q-Q Plot: {title}",
        xaxis_title="Theoretical Quantiles",
        yaxis_title="Sample Quantiles",
        height=300,
        showlegend=True
    )
    
    return fig


def _display_statistics(data):
    """
    Display detailed statistics for a data series.
    """
    stats_dict = {
        'Mean': f"{data.mean():.3f}",
        'Median': f"{data.median():.3f}",
        'Std Dev': f"{data.std():.3f}",
        'Min': f"{data.min():.3f}",
        'Max': f"{data.max():.3f}",
        'Skewness': f"{data.skew():.3f}",
        'Kurtosis': f"{data.kurtosis():.3f}"
    }
    
    for stat, value in stats_dict.items():
        cols = st.columns([1, 1])
        with cols[0]:
            st.markdown(f"**{stat}:**")
        with cols[1]:
            st.markdown(value)