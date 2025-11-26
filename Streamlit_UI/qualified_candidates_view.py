# qualified_candidates_view.py
# --------------------------------------------------------------
# Dedicated view for managing qualified candidates
# --------------------------------------------------------------

import streamlit as st
import requests
from components import section_header, skill_grid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_status_color(status):
    """Return color based on candidate status"""
    colors = {
        'NEW': '#6366f1',
        'REVIEWED': '#3b82f6',
        'CONTACTED': '#10b981',
        'INTERVIEWING': '#f59e0b',
        'HIRED': '#22c55e',
        'REJECTED': '#ef4444'
    }
    return colors.get(status, '#6366f1')


def render_candidate_card(candidate, api_base_url):
    """Render a single candidate card with update capabilities"""
    
    status_color = get_status_color(candidate['status'])
    
    # Card header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {status_color}15, {status_color}25);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid {status_color};
        '>
            <h3 style='margin:0; color:{status_color};'>
                {candidate['match_percentage']}% Match
                {'⭐' if candidate.get('is_highly_qualified', False) else ''}
            </h3>
            <p style='margin:0.3rem 0 0 0; color:#94a3b8;'>
                Status: <strong>{candidate['status']}</strong> | 
                Qualified: {candidate['qualification_date'][:10]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if candidate['is_contacted']:
            st.success("📞 Contacted")
        else:
            st.warning("📭 Not Contacted")
    
    with col3:
        if candidate.get('is_highly_qualified', False):
            st.info("⭐ Top Tier")
    
    # Expandable details
    with st.expander("📋 View Full Details", expanded=False):
        
        tab1, tab2, tab3 = st.tabs(["Overview", "Skills & Analysis", "Actions"])
        
        # Tab 1: Overview
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎓 Education")
                st.write(candidate.get('matching_education', 'N/A'))
                
                st.markdown("### 💼 Experience")
                st.write(candidate.get('matching_experience', 'N/A'))
            
            with col2:
                st.markdown("### 📊 Quick Stats")
                st.metric("Skills Match", len(candidate.get('matching_skills', [])))
                st.metric("Strengths", len(candidate.get('highlighted_strengths', [])))
                st.metric("Gaps", len(candidate.get('identified_gaps', [])))
        
        # Tab 2: Skills & Analysis
        with tab2:
            st.markdown("### 🎯 Matching Skills")
            skill_grid(candidate.get('matching_skills', []))
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💪 Key Strengths")
                for strength in candidate.get('highlighted_strengths', []):
                    st.markdown(f"✓ {strength}")
            
            with col2:
                st.markdown("### ⚠️ Areas for Improvement")
                for gap in candidate.get('identified_gaps', []):
                    st.markdown(f"• {gap}")
        
        # Tab 3: Actions
        with tab3:
            st.markdown("### 🔄 Update Candidate Status")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_status = st.selectbox(
                    "Status",
                    ["NEW", "REVIEWED", "CONTACTED", "INTERVIEWING", "HIRED", "REJECTED"],
                    index=["NEW", "REVIEWED", "CONTACTED", "INTERVIEWING", "HIRED", "REJECTED"].index(candidate['status']),
                    key=f"status_sel_{candidate['id']}"
                )
                
                new_contacted = st.checkbox(
                    "Mark as Contacted",
                    value=candidate['is_contacted'],
                    key=f"contact_chk_{candidate['id']}"
                )
            
            with col2:
                notes = st.text_area(
                    "Notes / Comments",
                    value=candidate.get('notes', ''),
                    height=100,
                    key=f"notes_txt_{candidate['id']}"
                )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("💾 Save Changes", key=f"save_{candidate['id']}", use_container_width=True):
                    # Update via API
                    try:
                        data = {
                            'status': new_status,
                            'is_contacted': new_contacted,
                            'notes': notes
                        }
                        
                        response = requests.patch(
                            f"{api_base_url}/qualified-candidates/{candidate['id']}/update/",
                            json=data,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("🔄 Refresh", key=f"refresh_{candidate['id']}", use_container_width=True):
                    st.rerun()


def render_stats_dashboard(stats):
    """Render statistics dashboard with charts"""
    
    section_header("Statistics Dashboard", "📊")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card' style='border-top: 4px solid #6366f1;'>
            <h3 style='color:#6366f1; font-size:2.5rem; margin:0; font-weight:900;'>
                {stats.get('total_qualified_candidates', 0)}
            </h3>
            <p style='color:#9ca3af; margin:0; font-weight:600;'>Total Qualified</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card' style='border-top: 4px solid #10b981;'>
            <h3 style='color:#10b981; font-size:2.5rem; margin:0; font-weight:900;'>
                {stats.get('highly_qualified_count', 0)}
            </h3>
            <p style='color:#9ca3af; margin:0; font-weight:600;'>Highly Qualified (>90%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card' style='border-top: 4px solid #3b82f6;'>
            <h3 style='color:#3b82f6; font-size:2.5rem; margin:0; font-weight:900;'>
                {stats.get('contacted_count', 0)}
            </h3>
            <p style='color:#9ca3af; margin:0; font-weight:600;'>Contacted</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card' style='border-top: 4px solid #f59e0b;'>
            <h3 style='color:#f59e0b; font-size:2.5rem; margin:0; font-weight:900;'>
                {stats.get('not_contacted_count', 0)}
            </h3>
            <p style='color:#9ca3af; margin:0; font-weight:600;'>Not Contacted</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    # Status breakdown pie chart
    with col1:
        st.markdown("### 📊 Candidate Status Distribution")
        
        status_data = stats.get('status_breakdown', {})
        if status_data:
            df = pd.DataFrame([
                {'Status': k, 'Count': v} 
                for k, v in status_data.items() if v > 0
            ])
            
            fig = px.pie(
                df,
                values='Count',
                names='Status',
                color='Status',
                color_discrete_map={
                    'NEW': '#6366f1',
                    'REVIEWED': '#3b82f6',
                    'CONTACTED': '#10b981',
                    'INTERVIEWING': '#f59e0b',
                    'HIRED': '#22c55e',
                    'REJECTED': '#ef4444'
                },
                hole=0.4
            )
            
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    # Contact status
    with col2:
        st.markdown("### 📞 Contact Status")
        
        contacted = stats.get('contacted_count', 0)
        not_contacted = stats.get('not_contacted_count', 0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Contacted', 'Not Contacted'],
                y=[contacted, not_contacted],
                marker=dict(color=['#10b981', '#ef4444']),
                text=[contacted, not_contacted],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#333')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Insights
    st.markdown("### 💡 Key Insights")
    
    total = stats.get('total_qualified_candidates', 0)
    if total > 0:
        highly_qualified_pct = (stats.get('highly_qualified_count', 0) / total) * 100
        contacted_pct = (stats.get('contacted_count', 0) / total) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"📊 **{highly_qualified_pct:.1f}%** of candidates have >90% match")
        
        with col2:
            st.info(f"📞 **{contacted_pct:.1f}%** have been contacted")
        
        with col3:
            hiring_rate = (status_data.get('HIRED', 0) / total) * 100 if total > 0 else 0
            st.success(f"✅ **{hiring_rate:.1f}%** hiring rate")
        
        # Warnings
        if contacted_pct < 50:
            st.warning("⚠️ Over 50% of qualified candidates haven't been contacted yet!")
        
        if status_data.get('NEW', 0) > 10:
            st.warning(f"⚠️ You have {status_data.get('NEW', 0)} new candidates waiting for review!")
    else:
        st.info("🎯 No qualified candidates yet. Start analyzing resumes to build your talent pool!")


def export_candidates_csv(candidates):
    """Export candidates to CSV"""
    df = pd.DataFrame(candidates)
    
    # Select relevant columns
    columns = [
        'id', 'match_percentage', 'status', 'is_contacted', 
        'qualification_date', 'matching_education', 'matching_experience'
    ]
    
    export_df = df[columns] if all(col in df.columns for col in columns) else df
    
    return export_df.to_csv(index=False)