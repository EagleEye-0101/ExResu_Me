from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListItem, ListFlowable, Paragraph, SimpleDocTemplate, Spacer

from resume_engine.schemas.resume import ResumeData
from resume_engine.utils.phone import format_phone_display


def export_pdf(resume: ResumeData, output_path: Path) -> Path:
    """Export single-column ATS-friendly PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    headline_style = ParagraphStyle(
        "Headline",
        parent=styles["Normal"],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName="Helvetica-Bold",
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
    )
    job_title_style = ParagraphStyle(
        "JobTitle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        spaceBefore=4,
    )

    story = []
    story.append(Paragraph(resume.full_name, title_style))

    contact_parts = [
        resume.email,
        format_phone_display(resume.phone_country_code, resume.phone),
    ]
    if resume.location:
        contact_parts.append(resume.location)
    if resume.linkedin:
        contact_parts.append(resume.linkedin)
    story.append(Paragraph(" | ".join(contact_parts), contact_style))

    if resume.headline:
        story.append(Paragraph(resume.headline, headline_style))

    if resume.summary:
        story.append(Paragraph("SUMMARY", section_style))
        story.append(Paragraph(resume.summary.replace("\n", "<br/>"), body_style))

    if resume.experience:
        story.append(Paragraph("EXPERIENCE", section_style))
        for exp in resume.experience:
            story.append(Paragraph(f"{exp.title} — {exp.company}", job_title_style))
            date_loc = f"{exp.start_date} – {exp.end_date}"
            if exp.location:
                date_loc += f" | {exp.location}"
            story.append(Paragraph(date_loc, body_style))
            if exp.bullets:
                items = [ListItem(Paragraph(b, body_style)) for b in exp.bullets]
                story.append(ListFlowable(items, bulletType="bullet", leftIndent=12))

    if resume.education:
        story.append(Paragraph("EDUCATION", section_style))
        for edu in resume.education:
            line = f"{edu.degree}"
            if edu.field:
                line += f" in {edu.field}"
            line += f" — {edu.institution}"
            if edu.graduation_date:
                line += f" ({edu.graduation_date})"
            story.append(Paragraph(line, body_style))

    if resume.skills:
        story.append(Paragraph("SKILLS", section_style))
        story.append(Paragraph(", ".join(resume.skills), body_style))

    if resume.certifications:
        story.append(Paragraph("CERTIFICATIONS", section_style))
        for cert in resume.certifications:
            line = cert.name
            if cert.issuer:
                line += f" — {cert.issuer}"
            if cert.date:
                line += f" ({cert.date})"
            story.append(Paragraph(line, body_style))

    story.append(Spacer(1, 0.2 * inch))
    doc.build(story)
    return output_path
