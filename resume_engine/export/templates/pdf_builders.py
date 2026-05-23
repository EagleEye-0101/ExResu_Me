"""Per-template PDF builders using ReportLab."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListItem, ListFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from resume_engine.export.legacy_classic import export_pdf_classic
from resume_engine.export.templates.base import contact_pairs
from resume_engine.export.templates.ats_rules import MODERN_ACCENT_RGB
from resume_engine.schemas.resume import ResumeData
from resume_engine.utils.phone import format_phone_display


def _base_doc(output_path: Path, margin: float = 0.75) -> tuple[SimpleDocTemplate, list]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=margin * inch,
        rightMargin=margin * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    return doc, []


def build_classic_pdf(resume: ResumeData, output_path: Path) -> Path:
    return export_pdf_classic(resume, output_path)


def build_professional_pdf(resume: ResumeData, output_path: Path) -> Path:
    """Professional PDF with contact table and education-first sections."""
    doc, story = _base_doc(output_path)
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle("Name", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=13)
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, leading=11)
    section = ParagraphStyle(
        "Section", parent=styles["Heading2"], fontSize=11, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4
    )
    bold = ParagraphStyle("Bold", parent=body, fontName="Helvetica-Bold")

    story.append(Paragraph(resume.full_name, name_style))
    pairs = contact_pairs(resume)
    if pairs:
        rows = []
        for i in range(0, len(pairs), 2):
            left = pairs[i]
            right = pairs[i + 1] if i + 1 < len(pairs) else ("", "")
            rows.append([
                Paragraph(f"<b>{left[0]}:</b> {left[1]}", small),
                Paragraph(f"<b>{right[0]}:</b> {right[1]}" if right[0] else "", small),
            ])
        tbl = Table(rows, colWidths=[3.25 * inch, 3.25 * inch])
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(tbl)
        story.append(Spacer(1, 6))

    if resume.summary:
        story.append(Paragraph(resume.summary.replace("\n", "<br/>"), body))
        story.append(Spacer(1, 4))

    def row_between(left: str, right: str) -> Table:
        t = Table([[Paragraph(left, bold), Paragraph(right, small)]], colWidths=[4 * inch, 2.5 * inch])
        t.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT")]))
        return t

    if resume.education:
        story.append(Paragraph("Education", section))
        for edu in resume.education:
            story.append(row_between(edu.institution, edu.graduation_date))
            deg = edu.degree + (f" — {edu.field}" if edu.field else "")
            story.append(Paragraph(deg, body))

    groups = resume.effective_skill_groups()
    if groups:
        story.append(Paragraph("Skills", section))
        for g in groups:
            story.append(Paragraph(f"<b>{g.label}</b> {', '.join(g.skills)}", body))

    if resume.experience:
        story.append(Paragraph("Professional Experience", section))
        for exp in resume.experience:
            story.append(row_between(exp.company, exp.location))
            story.append(row_between(exp.title, f"{exp.start_date} – {exp.end_date or 'Present'}"))
            if exp.bullets:
                items = [ListItem(Paragraph(b, body)) for b in exp.bullets]
                story.append(ListFlowable(items, bulletType="bullet", leftIndent=12))

    doc.build(story)
    return output_path


def build_modern_pdf(resume: ResumeData, output_path: Path) -> Path:
    doc, story = _base_doc(output_path)
    styles = getSampleStyleSheet()
    accent = colors.Color(MODERN_ACCENT_RGB[0] / 255, MODERN_ACCENT_RGB[1] / 255, MODERN_ACCENT_RGB[2] / 255)
    name_style = ParagraphStyle("Name", parent=styles["Heading1"], fontSize=18, textColor=accent, spaceAfter=4)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=13)
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
    section = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=accent,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4,
    )

    story.append(Paragraph(resume.full_name, name_style))
    contact = f"{resume.email} · {format_phone_display(resume.phone_country_code, resume.phone)}"
    if resume.linkedin:
        contact += f" · {resume.linkedin}"
    story.append(Paragraph(contact, small))
    if resume.headline:
        story.append(Paragraph(f"<b>{resume.headline}</b>", body))
    story.append(Spacer(1, 6))

    if resume.summary:
        story.append(Paragraph("PROFILE", section))
        story.append(Paragraph(resume.summary.replace("\n", "<br/>"), body))

    if resume.experience:
        story.append(Paragraph("EXPERIENCE", section))
        for exp in resume.experience:
            story.append(Paragraph(f"<b>{exp.title}</b>    {exp.start_date} – {exp.end_date or 'Present'}", body))
            story.append(Paragraph(f"{exp.company}" + (f" · {exp.location}" if exp.location else ""), small))
            if exp.bullets:
                items = [ListItem(Paragraph(b, body)) for b in exp.bullets]
                story.append(ListFlowable(items, bulletType="bullet", leftIndent=12))

    if resume.education:
        story.append(Paragraph("EDUCATION", section))
        for edu in resume.education:
            story.append(Paragraph(f"<b>{edu.institution}</b> — {edu.degree} ({edu.graduation_date})", body))

    if resume.skills or resume.skill_groups:
        story.append(Paragraph("SKILLS", section))
        groups = resume.effective_skill_groups()
        if groups:
            for g in groups:
                story.append(Paragraph(f"<b>{g.label}:</b> {', '.join(g.skills)}", body))
        else:
            story.append(Paragraph(", ".join(resume.skills), body))

    doc.build(story)
    return output_path


def build_compact_pdf(resume: ResumeData, output_path: Path) -> Path:
    doc, story = _base_doc(output_path, margin=0.6)
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle("Name", parent=styles["Heading1"], fontSize=13, spaceAfter=2)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=11)
    section = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=10, fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=2)

    header = Table(
        [
            [
                Paragraph(f"<b>{resume.full_name}</b>", name_style),
                Paragraph(
                    f"{resume.email} · {format_phone_display(resume.phone_country_code, resume.phone)}",
                    body,
                ),
            ]
        ],
        colWidths=[3 * inch, 3.5 * inch],
    )
    header.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(header)
    if resume.summary:
        story.append(Paragraph(resume.summary, body))
    if resume.experience:
        story.append(Paragraph("EXPERIENCE", section))
        for exp in resume.experience:
            story.append(
                Paragraph(
                    f"<b>{exp.title}</b>, {exp.company} ({exp.start_date}–{exp.end_date or 'Present'})",
                    body,
                )
            )
            for b in exp.bullets[:4]:
                story.append(Paragraph(f"• {b}", body))
    if resume.education:
        story.append(Paragraph("EDUCATION", section))
        for edu in resume.education:
            story.append(Paragraph(f"{edu.degree}, {edu.institution}", body))
    if resume.skills:
        story.append(Paragraph("SKILLS", section))
        story.append(Paragraph(" · ".join(resume.skills), body))
    doc.build(story)
    return output_path
