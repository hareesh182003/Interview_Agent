import datetime
import uuid
import requests


# ---------------------------------------------------------
# 🔵 API CALL WRAPPER
# ---------------------------------------------------------
def analyze_resume_api(api_url, resume_file, job_description):
    """Handles Django API interaction with proper error handling."""
    try:
        session = requests.Session()
        session.get(f"{api_url}/health/")  # warmup

        resume_file.seek(0)
        files = {"resume_file": (resume_file.name, resume_file, "application/pdf")}
        data = {"job_description": job_description}

        response = session.post(f"{api_url}/analyze/", files=files, data=data, timeout=60)

        if response.status_code == 201:
            return response.json(), None

        return None, f"API Error {response.status_code}: {response.text}"

    except requests.exceptions.ConnectionError:
        return None, "⚠️ Cannot connect to backend API."

    except Exception as e:
        return None, f"Unexpected Error: {str(e)}"


# ---------------------------------------------------------
# 🔵 UNIQUE SESSION GENERATOR
# ---------------------------------------------------------
def generate_session_id():
    return str(uuid.uuid4())


# ---------------------------------------------------------
# 🔵 PERCENT → COLOR MAPPING
# ---------------------------------------------------------
def score_to_color(score: float):
    """Return a color hex depending on score."""
    if score >= 80:
        return "#10b981"
    elif score >= 65:
        return "#f59e0b"
    elif score >= 50:
        return "#f97316"
    else:
        return "#ef4444"


# ---------------------------------------------------------
# 🔵 PERCENT → GRADIENT MAPPING
# ---------------------------------------------------------
def score_to_gradient(score: float):
    if score >= 80:
        return "linear-gradient(135deg, #10b981 0%, #34d399 100%)"
    elif score >= 65:
        return "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)"
    elif score >= 50:
        return "linear-gradient(135deg, #f97316 0%, #fb923c 100%)"
    else:
        return "linear-gradient(135deg, #ef4444 0%, #f87171 100%)"


# ---------------------------------------------------------
# 🔵 AUTO-UI DIRTY THEME BASED ON MATCH
# ---------------------------------------------------------
def score_to_ui_theme(score: float):
    """Theme colors auto-switch based on match score."""
    if score >= 80:
        return {
            "primary": "#10b981",
            "bg": "#062e27",
            "text": "white"
        }

    elif score >= 65:
        return {
            "primary": "#f59e0b",
            "bg": "#34280c",
            "text": "white"
        }

    elif score >= 50:
        return {
            "primary": "#f97316",
            "bg": "#3b2411",
            "text": "white"
        }

    else:
        return {
            "primary": "#ef4444",
            "bg": "#3b0d0d",
            "text": "white"
        }


# ---------------------------------------------------------
# 🔵 DATE FORMATTING
# ---------------------------------------------------------
def format_date(timestamp_str):
    try:
        dt = datetime.datetime.fromisoformat(timestamp_str.replace("Z", ""))
        return dt.strftime("%d %b %Y • %I:%M %p")
    except:
        return timestamp_str


# ---------------------------------------------------------
# 🔵 TEXT CLEANING
# ---------------------------------------------------------
def format_text_block(text: str):
    if not text:
        return "N/A"
    text = text.strip()
    text = text.replace("\n", "<br>")
    return text


# ---------------------------------------------------------
# 🔵 NORMALIZE SKILL LIST
# ---------------------------------------------------------
def normalize_skills(skills):
    """Ensures no duplicates, trims spaces, sorts alphabetically."""
    if not skills:
        return []
    cleaned = list({s.strip() for s in skills})
    return sorted(cleaned, key=lambda x: x.lower())


# ---------------------------------------------------------
# 🔵 SCORE CALCULATION HELPER FOR COMPARISON MODE
# ---------------------------------------------------------
def prepare_comparison_payload(results_list):
    """Convert multiple resume responses into a normalized structure."""
    payload = []
    for r in results_list:
        payload.append({
            "session_id": r["session_id"],
            "match": float(r["match_percentage"]),
            "skills": normalize_skills(r["matching_skills"]),
            "strengths": r.get("highlighted_strengths", []),
            "gaps": r.get("identified_gaps", []),
        })
    return payload


# ---------------------------------------------------------
# 🔵 QUALIFIED CANDIDATE HELPERS
# ---------------------------------------------------------
def is_qualified(match_percentage: float) -> bool:
    """Check if resume qualifies (>80%)"""
    return float(match_percentage) > 80.0


def is_highly_qualified(match_percentage: float) -> bool:
    """Check if resume is highly qualified (>90%)"""
    return float(match_percentage) >= 90.0


def get_qualification_tier(match_percentage: float) -> str:
    """Return qualification tier based on score"""
    score = float(match_percentage)
    if score >= 95:
        return "EXCEPTIONAL"
    elif score >= 90:
        return "HIGHLY QUALIFIED"
    elif score >= 85:
        return "STRONG MATCH"
    elif score > 80:
        return "QUALIFIED"
    else:
        return "NOT QUALIFIED"


def format_candidate_summary(candidate: dict) -> str:
    """Format candidate info for display"""
    return f"""
    Match: {candidate['match_percentage']}%
    Status: {candidate['status']}
    Skills: {len(candidate.get('matching_skills', []))}
    Qualified: {candidate['qualification_date'][:10]}
    """