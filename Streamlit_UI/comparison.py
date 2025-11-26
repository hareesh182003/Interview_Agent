# comparison.py
# --------------------------------------------------------------
# Multi-resume comparison: radar charts, overlap heatmap,
# score tables, & structured side-by-side layout.
# --------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from charts import comparison_radar
from components import comparison_card, section_header


# --------------------------------------------------------------
# 1. Compute skill overlap
# --------------------------------------------------------------

def compute_skill_overlap(resume_results: dict):
    """
    Input:
        {
            "Resume A": result_obj,
            "Resume B": result_obj,
            "Resume C": result_obj,
        }

    Returns:
        DataFrame for heatmap
    """
    names = list(resume_results.keys())
    matrix = []

    for i in names:
        row = []
        skills_i = set(resume_results[i]["matching_skills"])
        for j in names:
            skills_j = set(resume_results[j]["matching_skills"])
            overlap = len(skills_i & skills_j)
            total = len(skills_i | skills_j)
            score = overlap / total if total > 0 else 0
            row.append(round(score, 2))
        matrix.append(row)

    df = pd.DataFrame(matrix, index=names, columns=names)
    return df


# --------------------------------------------------------------
# 2. Skill Overlap Heatmap
# --------------------------------------------------------------

def overlap_heatmap(df):
    fig = px.imshow(
        df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Viridis",
        labels=dict(color="Overlap %"),
    )

    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
        coloraxis_colorbar=dict(title="Overlap"),
        font=dict(color="white")
    )

    return fig


# --------------------------------------------------------------
# 3. Match Score Table
# --------------------------------------------------------------

def score_table(resume_results: dict):
    rows = []

    for name, data in resume_results.items():
        rows.append({
            "Resume": name,
            "Match %": data["match_percentage"],
            "Skills": len(data["matching_skills"]),
            "Strengths": len(data["highlighted_strengths"]),
            "Gaps": len(data["identified_gaps"]),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Match %", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------------------
# 4. Comparison Radar Wrapper
# --------------------------------------------------------------

def comparison_radar_section(resume_results: dict):
    st.markdown("### 📡 Skill Fit Radar Comparison")

    radar_input = {}

    for name, data in resume_results.items():

        skills = data["matching_skills"]
        if not skills:
            continue

        # Normalize equal weights
        weights = [1] * len(skills)
        weights = np.array(weights) / max(weights)
        radar_input[name] = {"skills": skills, "weights": list(weights)}

    if radar_input:
        fig = comparison_radar(radar_input)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough skills available for radar comparison.")


# --------------------------------------------------------------
# 5. Side-by-Side Resume Cards
# --------------------------------------------------------------

def side_by_side_cards(resume_results: dict):
    names = list(resume_results.keys())

    st.markdown("### 🧩 Resume Comparison Summary")

    cols = st.columns(len(names))

    for col, name in zip(cols, names):
        with col:
            comparison_card(
                title=name,
                match_score=resume_results[name]["match_percentage"],
                color="#6366f1"
            )


# --------------------------------------------------------------
# 6. FULL COMPARISON VIEW
# --------------------------------------------------------------

def comparison_view(resume_results: dict):
    """
    Full comparison page (called by main app):
    - cards
    - table
    - radar
    - heatmap
    """

    section_header("Multi-Resume Comparison", "📊")

    # 1) Cards
    side_by_side_cards(resume_results)

    st.markdown("---")

    # 2) Scores Table
    st.markdown("### 📘 Match Score Summary")
    score_table(resume_results)

    st.markdown("---")

    # 3) Radar Chart Comparison
    comparison_radar_section(resume_results)

    st.markdown("---")

    # 4) Skill Overlap Heatmap
    df = compute_skill_overlap(resume_results)

    st.markdown("### 🔥 Skill Overlap Heatmap")
    st.plotly_chart(overlap_heatmap(df), use_container_width=True)
