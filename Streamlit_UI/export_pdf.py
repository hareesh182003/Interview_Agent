# export_pdf.py
# ----------------------------------------------------------------------
# Premium PDF Export Engine for ATS Resume Analyzer Pro
# ----------------------------------------------------------------------
# Generates branded PDF with:
# - Title header
# - Score donut (image)
# - Radar chart (image)
# - Skills table
# - Strengths & gaps
# - Experience summary
# ----------------------------------------------------------------------

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import inch
import io
import base64
from charts import score_donut, radar_chart_all_skills


# ----------------------------------------------------------------------
# Convert Plotly figure → PNG bytes (for embedding into PDF)
# ----------------------------------------------------------------------

def fig_to_png_bytes(fig):
    """Convert plotly figure to PNG bytes for PDF."""
    png_bytes = fig.to_image(format="png", width=900, height=700, scale=2)
    return io.BytesIO(png_bytes)


# ----------------------------------------------------------------------
# Core PDF Generator
# ----------------------------------------------------------------------

def generate_pdf(results: dict, output_path: str):
    """
    Generates a full ATS report PDF.
    results = API response dict.
    """

    # Extract data
    score = results["match_percentage"]
    skills = results["matching_skills"]
    strengths = results["highlighted_strengths"]
    gaps = results["identified_gaps"]
    education = results["matching_education"]
    experience = results["matching_experience"]
    session_id = results.get("session_id", "--")
    created = results.get("created_at", "--")

    # PDF Document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        title="ATS Resume Analyzer Pro - Report"
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=28,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=20,
    )
    header_style = ParagraphStyle(
        "Header",
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor("#4f46e5"),
        spaceAfter=12,
    )
    text_style = ParagraphStyle(
        "Text",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        fontSize=12,
        leading=16,
    )

    elements = []

    # ------------------------------------------------------------------
    # Title Block
    # ------------------------------------------------------------------
    elements.append(Paragraph("ATS Resume Analyzer Pro", title_style))
    elements.append(Paragraph("<b>Professional ATS Match Report</b>", styles["Heading3"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"<b>Match Score:</b> {score}%", text_style
    ))
    elements.append(Paragraph(
        f"<b>Generated On:</b> {created}", text_style
    ))
    elements.append(Paragraph(
        f"<b>Session ID:</b> {session_id}", text_style
    ))
    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # SCORE DONUT IMAGE
    # ------------------------------------------------------------------
    elements.append(Paragraph("Overall Score", header_style))

    donut_fig = score_donut(score)
    donut_img = fig_to_png_bytes(donut_fig)
    elements.append(Image(donut_img, width=300, height=300))
    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # RADAR CHART IMAGE
    # ------------------------------------------------------------------
    elements.append(Paragraph("Skill Fit Radar", header_style))

    if skills:
        radar_fig = radar_chart_all_skills(skills)
        radar_img = fig_to_png_bytes(radar_fig)
        elements.append(Image(radar_img, width=400, height=350))
        elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph("No skills available for radar visualization.", text_style))

    # ------------------------------------------------------------------
    # SKILLS TABLE
    # ------------------------------------------------------------------
    elements.append(Paragraph("Matched Skills", header_style))

    if skills:
        skill_data = [["Skill"]] + [[s] for s in skills]
        skill_table = Table(skill_data, colWidths=[350])
        skill_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#e5e7eb")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ]))
        elements.append(skill_table)
    else:
        elements.append(Paragraph("No matching skills found.", text_style))

    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # STRENGTHS TABLE
    # ------------------------------------------------------------------

    elements.append(Paragraph("Key Strengths", header_style))

    if strengths:
        strength_data = [["Strength"]] + [[s] for s in strengths]
        t = Table(strength_data, colWidths=[350])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#d1fae5")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No strong areas detected.", text_style))

    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # GAPS TABLE
    # ------------------------------------------------------------------

    elements.append(Paragraph("Improvement Areas", header_style))

    if gaps:
        gap_data = [["Gap"]] + [[g] for g in gaps]
        t = Table(gap_data, colWidths=[350])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ef4444")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fee2e2")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No major gaps detected.", text_style))

    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # EDUCATION + EXPERIENCE
    # ------------------------------------------------------------------

    elements.append(Paragraph("Education", header_style))
    elements.append(Paragraph(f"{education}", text_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("Experience Summary", header_style))
    elements.append(Paragraph(f"{experience}", text_style))
    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------------
    # FOOTER
    # ------------------------------------------------------------------

    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        "<i>Generated by ATS Resume Analyzer Pro — Smart Hiring Insights</i>",
        ParagraphStyle("footer", alignment=TA_CENTER, textColor=colors.grey, fontSize=10)
    ))

    # Build PDF
    doc.build(elements)

    return output_path
