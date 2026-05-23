"""Modern accent-bar template."""

from pathlib import Path

from resume_engine.export.templates.base import render_jinja
from resume_engine.export.templates.docx_builders import build_modern_docx
from resume_engine.export.templates.pdf_builders import build_modern_pdf
from resume_engine.schemas.resume import ResumeData


def render_html(resume: ResumeData) -> str:
    return render_jinja("modern.html", resume)


def export_docx(resume: ResumeData, output_path: Path) -> Path:
    return build_modern_docx(resume, output_path)


def export_pdf(resume: ResumeData, output_path: Path) -> Path:
    return build_modern_pdf(resume, output_path)
