# app.py
# ======================================================================
# ATS RESUME ANALYZER PRO — MAIN APPLICATION
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
    match_bar_item
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
    initial_sidebar_state="collapsed"
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


# ------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "comparison_data" not in st.session_state:
    st.session_state.comparison_data = {}


# ------------------------------------------------------
# LOAD THEME
# ------------------------------------------------------
if st.session_state.results:
    score = st.session_state.results["match_percentage"]
    st.markdown(load_theme(score), unsafe_allow_html=True)
else:
    st.markdown(load_theme(), unsafe_allow_html=True)


# ======================================================
# UI START
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
                result["session_id"] = str(uuid.uuid4())
                st.session_state.results = result
                st.rerun()
            else:
                st.error(err)


# ------------------------------------------------------
# RESULTS VIEW
# ------------------------------------------------------
else:
    results = st.session_state.results

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
    # TAB 1 — MATCH BREAKDOWN
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
    # TAB 2 — SKILLS
    # ===============================
    with tab2:
        section_header("Matching Skills", "🎯")
        skill_grid(results["matching_skills"])

        st.markdown("---")

        st.markdown("### 🔥 Skill Bars")
        for skill in results["matching_skills"]:
            match_bar_item(skill, 100)

    # ===============================
    # TAB 3 — STRENGTHS & GAPS
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
    # TAB 4 — EXPORT / COMPARE
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

