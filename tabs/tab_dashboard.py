"""
User Dashboard Tab
Shows user statistics, analysis history, and quick actions
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database.db_functions import get_user_analyses, get_user_stats, delete_analysis

def render_dashboard_tab():
    """
    Render user dashboard with statistics and history
    """
    st.markdown("## 📊 Your Dashboard")
    st.markdown("Track your data quality journey and view analysis history.")
    
    # Get user stats
    stats = get_user_stats()
    
    if stats.get('total_analyses', 0) == 0:
        st.info("📋 No analyses yet. Upload a CSV file to get started!")
        return
    
    # ==================== STATS CARDS ====================
    st.markdown("### 📈 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            ">
                <div style="font-size: 32px; font-weight: 700;">{stats['total_analyses']}</div>
                <div style="font-size: 14px; opacity: 0.9;">Total Analyses</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score = stats['avg_health_score']
        color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        st.markdown(f"""
            <div style="
                background: {color};
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            ">
                <div style="font-size: 32px; font-weight: 700;">{score}%</div>
                <div style="font-size: 14px; opacity: 0.9;">Avg Health Score</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
            ">
                <div style="font-size: 32px; font-weight: 700;">{stats['total_issues_found']}</div>
                <div style="font-size: 14px; opacity: 0.9;">Issues Found</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
            ">
                <div style="font-size: 32px; font-weight: 700;">{stats['files_analyzed']}</div>
                <div style="font-size: 14px; opacity: 0.9;">Files Analyzed</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== CHARTS ====================
    st.markdown("### 📊 Analysis Trends")
    
    analyses = get_user_analyses(limit=100)
    
    if len(analyses) > 1:
        # Convert to DataFrame
        df_analyses = pd.DataFrame(analyses)
        df_analyses['created_at'] = pd.to_datetime(df_analyses['created_at'])
        df_analyses = df_analyses.sort_values('created_at')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Health score trend
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=df_analyses['created_at'],
                y=df_analyses['health_score'],
                mode='lines+markers',
                name='Health Score',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))
            
            fig_trend.update_layout(
                title="Health Score Over Time",
                xaxis_title="Date",
                yaxis_title="Health Score (%)",
                height=300,
                template="plotly_dark",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Issues breakdown
            total_high = df_analyses['issues_high'].sum()
            total_medium = df_analyses['issues_medium'].sum()
            total_low = df_analyses['issues_low'].sum()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['High', 'Medium', 'Low'],
                values=[total_high, total_medium, total_low],
                marker=dict(colors=['#ef4444', '#f59e0b', '#10b981']),
                hole=0.4
            )])
            
            fig_pie.update_layout(
                title="Issues by Severity",
                height=300,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # ==================== ANALYSIS HISTORY ====================
    st.markdown("### 📋 Analysis History")
    
    # Search and filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search by filename", placeholder="Enter filename...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Recent", "Health Score", "Filename"])
    with col3:
        limit = st.number_input("Show", min_value=10, max_value=100, value=20, step=10)
    
    # Get analyses
    all_analyses = get_user_analyses(limit=limit)
    
    # Filter by search
    if search_query:
        all_analyses = [a for a in all_analyses if search_query.lower() in a['filename'].lower()]
    
    # Sort
    if sort_by == "Health Score":
        all_analyses = sorted(all_analyses, key=lambda x: x['health_score'], reverse=True)
    elif sort_by == "Filename":
        all_analyses = sorted(all_analyses, key=lambda x: x['filename'])
    # Recent is default (already sorted by created_at desc)
    
    # Display as table
    if all_analyses:
        for analysis in all_analyses:
            with st.expander(f"📄 {analysis['filename']} - {analysis['health_score']}% Health Score"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Health Score", f"{analysis['health_score']}%")
                with col2:
                    st.metric("Rows", f"{analysis['total_rows']:,}")
                with col3:
                    st.metric("Columns", analysis['total_columns'])
                with col4:
                    st.metric("Total Issues", 
                             analysis['issues_high'] + analysis['issues_medium'] + analysis['issues_low'])
                
                # Issue breakdown
                st.markdown("**Issues Breakdown:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"🔴 **High:** {analysis['issues_high']}")
                with col2:
                    st.markdown(f"🟠 **Medium:** {analysis['issues_medium']}")
                with col3:
                    st.markdown(f"🟢 **Low:** {analysis['issues_low']}")
                
                # Date and actions
                st.markdown(f"📅 **Analyzed:** {pd.to_datetime(analysis['created_at']).strftime('%Y-%m-%d %H:%M')}")
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{analysis['id']}"):
                    result = delete_analysis(analysis['id'])
                    if result['success']:
                        st.success("✅ Analysis deleted!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['error']}")
    else:
        st.info("No analyses found matching your search.")