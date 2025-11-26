# app.py
# ======================================================================
# ATS RESUME ANALYZER PRO – MAIN APPLICATION (with Qualified Candidates)
# ======================================================================

import streamlit as st
import requests
import uuid
import time
from datetime import datetime

from theme import load_theme
from components import (
    section_header,
    resume_summary_block,
    skill_grid,
    strength_card,
    gap_card,
    radar_section,
    match_bar_item,
    qualified_badge
)
from comparison import comparison_view
from export_pdf import generate_pdf


# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------
st.set_page_config(
    page_title="ATS Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000/api/django"


# ------------------------------------------------------
# HELPERS
# ------------------------------------------------------

def get_csrf(session):
    """Retrieve CSRF token from Django."""
    try:
        session.get(f"{API_BASE_URL}/health/")
        return session.cookies.get("csrftoken", None)
    except:
        return None


def analyze_resume_api(resume_file, job_description):
    session = requests.Session()
    csrf = get_csrf(session)

    resume_file.seek(0)
    files = {"resume_file": (resume_file.name, resume_file, "application/pdf")}
    data = {"job_description": job_description}
    headers = {"Referer": API_BASE_URL}

    if csrf:
        headers["X-CSRFToken"] = csrf

    try:
        r = session.post(
            f"{API_BASE_URL}/analyze/",
            files=files,
            data=data,
            headers=headers,
            timeout=120
        )

        if r.status_code == 201:
            return r.json(), None
        else:
            return None, f"Error {r.status_code}: {r.text}"

    except Exception as e:
        return None, str(e)


def get_qualified_candidates(status_filter=None, min_percentage=80):
    """Fetch qualified candidates from API"""
    try:
        params = {"min_percentage": min_percentage}
        if status_filter:
            params["status"] = status_filter
        
        response = requests.get(
            f"{API_BASE_URL}/qualified-candidates/",
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}"
    except Exception as e:
        return None, str(e)


def get_qualified_stats():
    """Get statistics about qualified candidates"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/qualified-candidates/stats/",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}"
    except Exception as e:
        return None, str(e)


def update_candidate_status(candidate_id, status=None, is_contacted=None, notes=None):
    """Update candidate status"""
    try:
        session = requests.Session()
        csrf = get_csrf(session)
        
        data = {}
        if status:
            data['status'] = status
        if is_contacted is not None:
            data['is_contacted'] = is_contacted
        if notes:
            data['notes'] = notes
        
        headers = {"Referer": API_BASE_URL}
        if csrf:
            headers["X-CSRFToken"] = csrf
        
        response = session.patch(
            f"{API_BASE_URL}/qualified-candidates/{candidate_id}/update/",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}"
    except Exception as e:
        return None, str(e)


# ------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "comparison_data" not in st.session_state:
    st.session_state.comparison_data = {}

if "current_page" not in st.session_state:
    st.session_state.current_page = "analyzer"


# ------------------------------------------------------
# LOAD THEME
# ------------------------------------------------------
if st.session_state.results:
    score = st.session_state.results["match_percentage"]
    st.markdown(load_theme(score), unsafe_allow_html=True)
else:
    st.markdown(load_theme(), unsafe_allow_html=True)


# ======================================================
# SIDEBAR NAVIGATION
# ======================================================

with st.sidebar:
    st.markdown("### 🎯 Navigation")
    
    if st.button("📊 Resume Analyzer", use_container_width=True):
        st.session_state.current_page = "analyzer"
        st.rerun()
    
    if st.button("⭐ Qualified Candidates", use_container_width=True):
        st.session_state.current_page = "qualified"
        st.rerun()
    
    if st.button("📈 Statistics", use_container_width=True):
        st.session_state.current_page = "stats"
        st.rerun()
    
    st.markdown("---")
    
    # Display current stats in sidebar
    stats, err = get_qualified_stats()
    if stats:
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Qualified", stats.get('total_qualified_candidates', 0))
        st.metric("Highly Qualified (>90%)", stats.get('highly_qualified_count', 0))
        st.metric("Not Contacted", stats.get('not_contacted_count', 0))


# ======================================================
# PAGE ROUTING
# ======================================================

if st.session_state.current_page == "analyzer":
    # ======================================================
    # ANALYZER PAGE
    # ======================================================
    
    section_header("ATS Resume Analyzer Pro", "🎯")
    
    st.markdown(
        "<p style='text-align:center; color:#94a3b8;'>AI-powered resume & job match analysis</p>",
        unsafe_allow_html=True
    )
    
    # ------------------------------------------------------
    # MAIN VIEW (NO RESULTS YET)
    # ------------------------------------------------------
    if st.session_state.results is None:
    
        col1, col2 = st.columns([1, 1])
    
        # =====================
        # RESUME UPLOAD
        # =====================
        with col1:
            st.markdown("### 📄 Upload Your Resume")
    
            st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Upload PDF resume",
                type=["pdf"],
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
    
            if uploaded_file:
                st.success(f"Uploaded: {uploaded_file.name}")
    
        # =====================
        # JOB DESCRIPTION
        # =====================
        with col2:
            st.markdown("### 💼 Enter Job Description")
    
            job_description = st.text_area(
                "Paste Job Description",
                height=300,
                placeholder="Paste full job description..."
            )
    
        st.markdown("---")
    
        # =====================
        # ACTION BUTTON
        # =====================
        analyze_btn = st.button(
            "🚀 Run ATS Analysis",
            type="primary",
            disabled=not (uploaded_file and job_description.strip()),
            use_container_width=True
        )
    
        if analyze_btn:
            with st.spinner("Analyzing your resume..."):
                result, err = analyze_resume_api(uploaded_file, job_description)
    
                if result:
                    st.session_state.results = result
                    
                    # Show qualification notification
                    if result.get("is_qualified", False):
                        st.success("🎉 Congratulations! This resume qualifies (>80% match) and has been saved to the Qualified Candidates database!")
                    
                    st.rerun()
                else:
                    st.error(err)
    
    
    # ------------------------------------------------------
    # RESULTS VIEW
    # ------------------------------------------------------
    else:
        results = st.session_state.results
        
        # Show qualification badge if qualified
        if results.get("is_qualified", False):
            qualified_badge(results["match_percentage"])
    
        # Summary Top Section
        resume_summary_block(results)
    
        # ------------------------------------------
        # Tabs
        # ------------------------------------------
        tab1, tab2, tab3, tab4 = st.tabs([
            "Match Breakdown",
            "Skills",
            "Strengths & Gaps",
            "Export / Compare"
        ])
    
        # ===============================
        # TAB 1 – MATCH BREAKDOWN
        # ===============================
        with tab1:
            section_header("Match Breakdown", "📊")
    
            st.markdown("### 🎓 Education Match")
            st.info(results["matching_education"])
            st.markdown("<br>", unsafe_allow_html=True)
    
            st.markdown("### 💼 Experience Match")
            st.info(results["matching_experience"])
            st.markdown("<br>", unsafe_allow_html=True)
    
            st.markdown("### 📡 Radar (Skill Fit)")
            radar_section(results["matching_skills"])
    
        # ===============================
        # TAB 2 – SKILLS
        # ===============================
        with tab2:
            section_header("Matching Skills", "🎯")
            skill_grid(results["matching_skills"])
    
            st.markdown("---")
    
            st.markdown("### 🔥 Skill Bars")
            for skill in results["matching_skills"]:
                match_bar_item(skill, 100)
    
        # ===============================
        # TAB 3 – STRENGTHS & GAPS
        # ===============================
        with tab3:
            section_header("Key Strengths", "💪")
    
            for s in results["highlighted_strengths"]:
                strength_card(s)
    
            st.markdown("---")
    
            section_header("Gaps / Improvement Areas", "⚠️")
    
            for g in results["identified_gaps"]:
                gap_card(g)
    
        # ===============================
        # TAB 4 – EXPORT / COMPARE
        # ===============================
        with tab4:
    
            section_header("Export & Compare", "📤")
    
            # -------------------------
            # PDF EXPORT
            # -------------------------
            st.markdown("### 📄 Download PDF Report")
    
            pdf_path = f"ATS_Report_{results['session_id']}.pdf"
    
            if st.button("Generate PDF Report", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    generate_pdf(results, pdf_path)
    
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Report",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf",
                        use_container_width=True
                    )
    
            st.markdown("---")
    
            # -------------------------
            # ADD TO COMPARISON
            # -------------------------
            if st.button("➕ Add to Comparison", use_container_width=True):
                name = f"Resume {len(st.session_state.comparison_data)+1}"
                st.session_state.comparison_data[name] = results
                st.success(f"Added as {name}")
    
            if st.session_state.comparison_data:
                st.markdown("### 🧩 Compare Multiple Resumes")
    
                if st.button("Open Comparison Mode", use_container_width=True):
                    comparison_view(st.session_state.comparison_data)
    
    
        st.markdown("---")
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.results = None
            st.rerun()


elif st.session_state.current_page == "qualified":
    # ======================================================
    # QUALIFIED CANDIDATES PAGE
    # ======================================================
    
    section_header("Qualified Candidates (>80% Match)", "⭐")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "NEW", "REVIEWED", "CONTACTED", "INTERVIEWING", "HIRED", "REJECTED"]
        )
    
    with col2:
        min_percentage = st.slider("Minimum Match %", 80, 100, 80)
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Fetch candidates
    status_param = None if status_filter == "All" else status_filter
    candidates, err = get_qualified_candidates(status_param, min_percentage)
    
    if err:
        st.error(f"Error loading candidates: {err}")
    elif not candidates:
        st.info("No qualified candidates found matching the filters.")
    else:
        st.markdown(f"### Found {len(candidates)} Qualified Candidates")
        
        # Display candidates in cards
        for candidate in candidates:
            with st.expander(
                f"🎯 {candidate.get('match_percentage', 0)}% Match - {candidate.get('status', 'NEW')} "
                f"{'⭐' if candidate.get('is_highly_qualified', False) else ''}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Match Score:** {candidate.get('match_percentage', 0)}%")
                    st.markdown(f"**Status:** {candidate.get('status', 'N/A')}")
                    st.markdown(f"**Contacted:** {'Yes ✓' if candidate.get('is_contacted') else 'No ✗'}")
                    st.markdown(f"**Qualification Date:** {candidate.get('qualification_date', '')[:10]}")
                    
                    if candidate.get('is_highly_qualified'):
                        st.success("⭐ Highly Qualified (>90%)")
                    
                    st.markdown("---")

                    # SAFE SKILLS
                    st.markdown("**Matching Skills:**")
                    skill_grid(candidate.get('matching_skills', []))

                    # SAFE STRENGTHS
                    st.markdown("**Strengths:**")
                    for strength in candidate.get('highlighted_strengths', []):
                        st.markdown(f"- {strength}")

                    # SAFE GAPS
                    st.markdown("**Gaps:**")
                    for gap in candidate.get('identified_gaps', []):
                        st.markdown(f"- {gap}")
                
                with col2:
                    st.markdown("### Update Status")
                    
                    new_status = st.selectbox(
                        "Change Status",
                        ["NEW", "REVIEWED", "CONTACTED", "INTERVIEWING", "HIRED", "REJECTED"],
                        index=["NEW", "REVIEWED", "CONTACTED", "INTERVIEWING", "HIRED", "REJECTED"]
                            .index(candidate.get('status', 'NEW')),
                        key=f"status_{candidate.get('id')}"
                    )
                    
                    new_contacted = st.checkbox(
                        "Mark as Contacted",
                        value=candidate.get('is_contacted', False),
                        key=f"contacted_{candidate.get('id')}"
                    )
                    
                    notes = st.text_area(
                        "Notes",
                        value=candidate.get('notes', ''),
                        key=f"notes_{candidate.get('id')}"
                    )
                    
                    if st.button("💾 Update", key=f"update_{candidate.get('id')}", use_container_width=True):
                        result, err = update_candidate_status(
                            candidate.get('id'),
                            status=new_status,
                            is_contacted=new_contacted,
                            notes=notes
                        )
                        
                        if result:
                            st.success("✅ Updated successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Error: {err}")



elif st.session_state.current_page == "stats":
    # ======================================================
    # STATISTICS PAGE
    # ======================================================
    
    section_header("Qualified Candidates Statistics", "📈")
    
    stats, err = get_qualified_stats()
    
    if err:
        st.error(f"Error loading statistics: {err}")
    elif stats:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Qualified",
                stats.get('total_qualified_candidates', 0),
                help="Candidates with >80% match"
            )
        
        with col2:
            st.metric(
                "Highly Qualified",
                stats.get('highly_qualified_count', 0),
                help="Candidates with >90% match"
            )
        
        with col3:
            st.metric(
                "Contacted",
                stats.get('contacted_count', 0)
            )
        
        with col4:
            st.metric(
                "Not Contacted",
                stats.get('not_contacted_count', 0)
            )
        
        st.markdown("---")
        
        # Status breakdown
        st.markdown("### 📊 Status Breakdown")
        
        status_data = stats.get('status_breakdown', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🆕 New", status_data.get('NEW', 0))
            st.metric("📋 Reviewed", status_data.get('REVIEWED', 0))
        
        with col2:
            st.metric("📞 Contacted", status_data.get('CONTACTED', 0))
            st.metric("💼 Interviewing", status_data.get('INTERVIEWING', 0))
        
        with col3:
            st.metric("✅ Hired", status_data.get('HIRED', 0))
            st.metric("❌ Rejected", status_data.get('REJECTED', 0))
        
        st.markdown("---")
        
        # Additional insights
        st.markdown("### 💡 Insights")
        
        total = stats.get('total_qualified_candidates', 0)
        if total > 0:
            highly_qualified_pct = (stats.get('highly_qualified_count', 0) / total) * 100
            contacted_pct = (stats.get('contacted_count', 0) / total) * 100
            
            st.info(f"📊 {highly_qualified_pct:.1f}% of qualified candidates have >90% match")
            st.info(f"📞 {contacted_pct:.1f}% of qualified candidates have been contacted")
            
            if contacted_pct < 50:
                st.warning("⚠️ Over 50% of qualified candidates haven't been contacted yet!")
        else:
            st.info("No qualified candidates yet. Start analyzing resumes to build your talent pool!")