# charts.py
# --------------------------------------------------------------
# All charts for ATS Analyzer Pro (Plotly + Streamlit)
# --------------------------------------------------------------

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np


# --------------------------------------------------------------
# 1. DONUT SCORE CHART
# --------------------------------------------------------------

def score_donut(match_score: float):
    """
    Creates a premium animated donut chart representing the match score.
    """

    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[match_score, 100 - match_score],
        hole=0.7,
        marker=dict(colors=["#6366f1", "#1e1f23"]),
        textinfo='none'
    ))

    fig.update_layout(
        height=300,
        width=300,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{match_score:.0f}%</b>",
                font=dict(size=36, color="white"),
                showarrow=False
            )
        ]
    )

    return fig


# --------------------------------------------------------------
# 2. RADAR CHART  (Option B: ALL Matching Skills)
# --------------------------------------------------------------

def radar_chart_all_skills(skills: list, weights=None):
    """
    Radar chart using ALL matched skills from the analysis.
    Skills are evenly normalized.
    """

    if not skills:
        return go.Figure()

    N = len(skills)

    # If no weights provided, assign normalized equal weights
    if weights is None:
        weights = np.ones(N)

    # Normalize
    max_value = max(weights)
    normalized = [float(w) / max_value for w in weights]

    categories = skills + [skills[0]]  # close shape
    values = list(normalized) + [normalized[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line=dict(color="#8b5cf6", width=3),
        fillcolor="rgba(139,92,246,0.3)"
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="#121317",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(color="white"),
                gridcolor="#333",
                linecolor="#444"
            ),
            angularaxis=dict(
                tickfont=dict(color="white"),
                gridcolor="#333",
                linecolor="#444"
            )
        ),
        height=560,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )

    return fig


# --------------------------------------------------------------
# 3. CIRCULAR SKILL PROGRESS RINGS
# --------------------------------------------------------------

def skill_ring(skill_name: str, percent: float):
    """
    Creates a circular progress ring for individual skill match %.
    """
    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=[percent, 100 - percent],
        hole=0.65,
        direction="clockwise",
        sort=False,
        marker=dict(colors=["#10b981", "#1e1f23"]),
        textinfo="none"
    ))

    fig.update_layout(
        height=230,
        width=230,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        annotations=[
            dict(text=f"<b>{percent:.0f}%</b>", font=dict(size=26, color="white"), showarrow=False),
            dict(text=f"{skill_name}", y=0.1, font=dict(size=16, color="#cbd5e1"), showarrow=False)
        ]
    )

    return fig


# --------------------------------------------------------------
# 4. HORIZONTAL MATCH BAR ANIMATION
# --------------------------------------------------------------

def match_bar(label: str, percent: float):
    """
    Horizontal bar chart showing skill or gap weight.
    """

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[percent],
        y=[label],
        orientation='h',
        marker=dict(
            color="#6366f1",
            line=dict(color="#8b5cf6", width=2)
        ),
        text=[f"{percent}%"],
        textposition="outside"
    ))

    fig.update_layout(
        height=90,
        margin=dict(l=40, r=20, t=20, b=20),
        xaxis=dict(range=[0, 100], showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=True),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig


# --------------------------------------------------------------
# 5. MULTI-RESUME COMPARISON RADAR
# --------------------------------------------------------------

def comparison_radar(resume_data: dict):
    """
    resume_data structure:
    {
        "Resume A": {"skills": [...], "weights": [...]},
        "Resume B": {"skills": [...], "weights": [...]}
    }
    """

    fig = go.Figure()
    categories = None

    for name, data in resume_data.items():

        skills = data["skills"]
        weights = data["weights"]
        N = len(skills)

        # close chart shape
        if categories is None:
            categories = skills + [skills[0]]

        values = weights + [weights[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=name,
            line=dict(width=2),
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#121317",
            radialaxis=dict(range=[0, 1], showgrid=True, gridcolor="#444", tickfont=dict(color="white")),
            angularaxis=dict(showgrid=True, gridcolor="#444", tickfont=dict(color="white"))
        ),
        height=620,
        legend=dict(font=dict(color="white"))
    )

    return fig
