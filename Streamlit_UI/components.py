# components.py
# --------------------------------------------------------------
# Modular UI components for ATS Resume Analyzer Pro
# --------------------------------------------------------------

import streamlit as st
from charts import score_donut, radar_chart_all_skills, skill_ring, match_bar
import uuid


# --------------------------------------------------------------
# HELPER: unique key generator
# --------------------------------------------------------------

def key():
    return str(uuid.uuid4())


# --------------------------------------------------------------
# 1. SECTION HEADER
# --------------------------------------------------------------

def section_header(title: str, emoji="🎯"):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        padding: 1.2rem;
        border-radius: 14px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    ">
        <h2 style='color:white; margin:0; font-weight:800;'>{emoji} {title}</h2>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------
# 2. SCORE CIRCLE COMPONENT
# --------------------------------------------------------------

def score_circle(match_score: float):
    st.markdown(
        "<h3 style='text-align:center; font-weight:700; color:#cbd5e1;'>Overall Match Score</h3>",
        unsafe_allow_html=True
    )
    st.plotly_chart(score_donut(match_score), use_container_width=True)


# --------------------------------------------------------------
# 3. STAT CARD (Animated)
# --------------------------------------------------------------

def stat_card(label: str, value: str, color: str = "#10b981"):
    st.markdown(f"""
        <div class="stat-card" style="border-top: 4px solid {color};">
            <h3 style="color:{color}; font-size:2.5rem; margin:0; font-weight:900;">{value}</h3>
            <p style="color:#9ca3af; margin:0; font-weight:600;">{label}</p>
        </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------
# 4. SKILL BADGES GRID
# --------------------------------------------------------------

def skill_grid(skills: list):
    if not skills:
        st.warning("No matching skills found.")
        return

    st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
    for skill in skills:
        st.markdown(f"<span class='skill-badge'>{skill}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------
# 5. STRENGTH/GAP CARDS
# --------------------------------------------------------------

def strength_card(text: str):
    st.markdown(f"""
    <div style='
        background: rgba(16,185,129,0.12);
        border-left: 5px solid #10b981;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
    '>
        <strong style='color:#10b981;'>{text}</strong>
        <p style='color:#0fb981cc; font-size:0.9rem; margin-top:0.3rem;'>Highly relevant to job requirements</p>
    </div>
    """, unsafe_allow_html=True)


def gap_card(text: str):
    st.markdown(f"""
    <div style='
        background: rgba(239,68,68,0.12);
        border-left: 5px solid #ef4444;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
    '>
        <strong style='color:#ef4444;'>{text}</strong>
        <p style='color:#ef4444cc; font-size:0.9rem; margin-top:0.3rem;'>Consider improving this area</p>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------------------
# 6. RADAR CHART SECTION
# --------------------------------------------------------------

def radar_section(skills: list):
    st.markdown("<h3 style='color:#e2e8f0; margin-top:1.5rem;'>Skill Fit Radar</h3>", unsafe_allow_html=True)

    weights = [1] * len(skills)
    fig = radar_chart_all_skills(skills, weights)

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------------------
# 7. MATCH BAR (horizontal)
# --------------------------------------------------------------

def match_bar_item(label: str, percent: float):
    st.plotly_chart(match_bar(label, percent), use_container_width=True)


# --------------------------------------------------------------
# 8. SINGLE RESUME SUMMARY BLOCK
# --------------------------------------------------------------

def resume_summary_block(results):
    match = results["match_percentage"]
    skills = results["matching_skills"]
    strengths = results["highlighted_strengths"]
    gaps = results["identified_gaps"]

    # Score circle
    score_circle(match)

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stat_card("Matching Skills", len(skills), "#10b981")

    with col2:
        stat_card("Strength Areas", len(strengths), "#3b82f6")

    with col3:
        stat_card("Improvement Areas", len(gaps), "#f59e0b")

    with col4:
        exp = results.get("matching_experience", "N/A")
        exp_value = exp.split()[0] if exp != "N/A" else "N/A"
        stat_card("Experience Match", exp_value, "#8b5cf6")

    st.markdown("---")


# --------------------------------------------------------------
# 9. COMPARISON CARD
# --------------------------------------------------------------

def comparison_card(title: str, match_score: float, color="#6366f1"):
    st.markdown(f"""
        <div class='compare-card'>
            <h3 style='color:{color}; margin:0; font-size:1.4rem; font-weight:700;'>{title}</h3>
            <p style='color:#94a3b8; margin-top:0.5rem;'>Match Score:</p>
            <h1 style='color:{color}; margin-top:-5px; font-size:3rem;'>{match_score:.0f}%</h1>
        </div>
    """, unsafe_allow_html=True)
