# comparison.py
# --------------------------------------------------------------
# Multi-resume comparison: radar charts, overlap heatmap,
# score tables, card animations, removal, undo, rename.
# --------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from charts import comparison_radar
from components import comparison_card, section_header


# ==============================================================
# SESSION STATE INIT
# ==============================================================

def _init_state(resume_results):
    """Ensures resume results & undo buffer exist."""
    if "resume_results" not in st.session_state:
        st.session_state.resume_results = resume_results

    if "undo_buffer" not in st.session_state:
        st.session_state.undo_buffer = None


# ==============================================================
# 1. Compute skill overlap matrix
# ==============================================================

def compute_skill_overlap(resume_results: dict):
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


# ==============================================================
# 2. Heatmap
# ==============================================================

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


# ==============================================================
# 3. Score Table
# ==============================================================

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


# ==============================================================
# 4. Radar Chart Comparison
# ==============================================================

def comparison_radar_section(resume_results: dict):
    st.markdown("### 📡 Skill Fit Radar Comparison")

    radar_input = {}

    for name, data in resume_results.items():
        skills = data["matching_skills"]
        if not skills:
            continue

        weights = np.array([1] * len(skills))
        weights = weights / max(weights)
        radar_input[name] = {"skills": skills, "weights": list(weights)}

    if radar_input:
        fig = comparison_radar(radar_input)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough skills available for radar comparison.")


# ==============================================================
# 5. Side-by-Side Cards (Remove / Rename / Undo / Remove All)
# ==============================================================

def side_by_side_cards():
    resume_results = st.session_state.resume_results
    names = list(resume_results.keys())

    st.markdown("### 🧩 Resume Comparison Summary")

    # Top bar for global actions
    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("🗑️ Remove ALL Resumes", key="remove_all"):
            st.session_state.undo_buffer = resume_results.copy()
            st.session_state.resume_results = {}
            st.warning("🗑️ All resumes removed!")
            st.rerun()

    with colB:
        if st.button("↩️ Undo Last Delete", key="undo_delete"):
            if st.session_state.undo_buffer:
                st.session_state.resume_results = st.session_state.undo_buffer
                st.session_state.undo_buffer = None
                st.success("♻️ Restored deleted resumes!")
                st.rerun()
            else:
                st.info("Nothing to undo.")

    # Show resume cards
    columns = st.columns(len(names) if names else 1)

    to_delete = None
    renamed_name = None
    new_name = None

    for col, name in zip(columns, names):
        data = resume_results[name]

        with col:
            comparison_card(
                title=name,
                match_score=data["match_percentage"],
                color="#6366f1"
            )

            # Rename input
            new_label = st.text_input(f"Rename {name}", value=name, key=f"rename_{name}")
            if new_label != name:
                renamed_name = name
                new_name = new_label

            # Delete button
            if st.button(f"❌ Remove", key=f"remove_{name}"):
                to_delete = name

    # Handle deletion after layout renders
    if to_delete:
        st.session_state.undo_buffer = resume_results.copy()
        del resume_results[to_delete]
        st.session_state.resume_results = resume_results
        st.success(f"🗑️ Removed **{to_delete}**")
        st.rerun()

    # Handle rename after layout
    if renamed_name and new_name and new_name.strip():
        if new_name not in resume_results:
            st.session_state.undo_buffer = resume_results.copy()
            resume_results[new_name] = resume_results.pop(renamed_name)
            st.session_state.resume_results = resume_results
            st.success(f"✏️ Renamed **{renamed_name} → {new_name}**")
            st.rerun()
        else:
            st.error("⚠️ A resume with that name already exists.")


# ==============================================================
# 6. FULL COMPARISON VIEW
# ==============================================================

def comparison_view(resume_results: dict):

    # Setup session state if not already
    _init_state(resume_results)

    rr = st.session_state.resume_results

    section_header("Multi-Resume Comparison", "📊")

    # 1 — Summary cards with tools
    side_by_side_cards()

    if not rr:
        st.info("No resumes remaining. Add more to compare.")
        return

    st.markdown("---")

    # 2 — Score Table
    st.markdown("### 📘 Match Score Summary")
    score_table(rr)

    st.markdown("---")

    # 3 — Radar Chart
    comparison_radar_section(rr)

    st.markdown("---")

    # 4 — Heatmap
    df = compute_skill_overlap(rr)
    st.markdown("### 🔥 Skill Overlap Heatmap")
    st.plotly_chart(overlap_heatmap(df), use_container_width=True)
