# theme.py
# ---------------------------------------------------------
# GLOBAL PREMIUM THEME + ANIMATIONS FOR STREAMLIT UI
# ---------------------------------------------------------

def load_theme(match_score=None):
    """
    Injects all CSS for the UI.
    If match_score is provided, dynamically adjust theme colors.
    """

    # Dynamic color theme based on match score
    if match_score is not None:
        if match_score >= 80:
            primary = "#10b981"
            primary_bg = "rgba(16,185,129,0.15)"
        elif match_score >= 65:
            primary = "#f59e0b"
            primary_bg = "rgba(245,158,11,0.15)"
        elif match_score >= 50:
            primary = "#f97316"
            primary_bg = "rgba(249,115,22,0.18)"
        else:
            primary = "#ef4444"
            primary_bg = "rgba(239,68,68,0.15)"
    else:
        # Default purple theme
        primary = "#6366f1"
        primary_bg = "rgba(99,102,241,0.15)"

    return f"""
<style>

:root {{
    --primary: {primary};
    --primary-bg: {primary_bg};
    --text-primary: #f3f4f6;
    --text-secondary: #a4a8ae;
    --bg-main: #0d0f12;
    --bg-card: #181b20;
    --bg-hover: #24272d;
    --radius: 14px;
    --shadow-soft: 0 4px 20px rgba(0,0,0,0.35);
}}

html, body, .main {{
    background: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif;
}}

/* -------------------------------------------------------------
   HEADERS
------------------------------------------------------------- */
h1 {{
    background: linear-gradient(135deg, #8b5cf6, var(--primary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900 !important;
}}

h2, h3 {{
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}}

/* -------------------------------------------------------------
   BUTTONS
------------------------------------------------------------- */
.stButton>button {{
    width: 100%;
    background: linear-gradient(135deg, var(--primary), #7c3aed);
    color: white !important;
    padding: 0.9rem 2rem;
    border-radius: var(--radius);
    border: 1px solid rgba(255,255,255,0.1);
    font-weight: 700;
    font-size: 1.05rem;
    box-shadow: var(--shadow-soft);
    transition: 0.25s ease;
}}

.stButton>button:hover {{
    background: linear-gradient(135deg, #7c3aed, var(--primary));
    transform: translateY(-4px);
}}

.stButton>button:disabled {{
    background: #2e2f33 !important;
    color: #777 !important;
}}

/* -------------------------------------------------------------
   ANIMATED CARDS
------------------------------------------------------------- */
.stat-card {{
    background: var(--bg-card);
    padding: 1.4rem;
    border-radius: var(--radius);
    border: 1px solid #24272d;
    box-shadow: var(--shadow-soft);
    transition: 0.3s ease;
    animation: fadeInUp 0.9s ease;
}}

.stat-card:hover {{
    background: var(--bg-hover);
    transform: translateY(-6px) scale(1.02);
}}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* -------------------------------------------------------------
   SKILL BADGES
------------------------------------------------------------- */
.skill-badge {{
    display: inline-block;
    background: var(--primary-bg);
    color: var(--primary);
    padding: 0.45rem 1.1rem;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    font-weight: 600;
    margin: 0.25rem;
    transition: 0.2s ease;
}}

.skill-badge:hover {{
    background: rgba(255,255,255,0.15);
    transform: scale(1.06);
}}

/* -------------------------------------------------------------
   UPLOAD BOX
------------------------------------------------------------- */
.upload-box {{
    border: 2px dashed var(--text-secondary);
    border-radius: 18px;
    padding: 3rem 2rem;
    text-align: center;
    background: #121317;
    transition: 0.3s ease;
}}

.upload-box:hover {{
    border-color: var(--primary);
    background: #1c1d21;
    transform: translateY(-4px);
}}

/* -------------------------------------------------------------
   SCORE CIRCLE
------------------------------------------------------------- */
.score-circle {{
    width: 240px;
    height: 240px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: var(--shadow-soft);
    animation: pulseGlow 2s infinite ease-in-out;
}}

.score-inner {{
    width: 190px;
    height: 190px;
    background: #0f1014;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: inset 0 4px 12px rgba(0,0,0,0.5);
}}

@keyframes pulseGlow {{
    0%   {{ box-shadow: 0 0 0px var(--primary); }}
    50%  {{ box-shadow: 0 0 24px var(--primary); }}
    100% {{ box-shadow: 0 0 0px var(--primary); }}
}}

/* -------------------------------------------------------------
   COMPARISON MODE LAYOUT
------------------------------------------------------------- */
.compare-card {{
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 1.2rem;
    border: 1px solid #24272d;
    box-shadow: var(--shadow-soft);
    transition: 0.25s ease;
    animation: fadeInUp 0.9s ease;
}}

.compare-card:hover {{
    background: var(--bg-hover);
    transform: translateY(-6px);
}}

/* -------------------------------------------------------------
   RADAR CHART CONTAINER
------------------------------------------------------------- */
.radar-container {{
    background: var(--bg-card);
    padding: 1rem;
    border-radius: var(--radius);
    margin-top: 1rem;
}}

</style>
"""
