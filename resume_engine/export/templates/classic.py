"""Classic centered resume template."""

from pathlib import Path

from resume_engine.export.templates.base import render_jinja
from resume_engine.export.templates.docx_builders import build_classic_docx
from resume_engine.export.templates.pdf_builders import build_classic_pdf
from resume_engine.schemas.resume import ResumeData


def render_html(resume: ResumeData) -> str:
    return render_jinja("classic.html", resume)


def export_docx(resume: ResumeData, output_path: Path) -> Path:
    return build_classic_docx(resume, output_path)


def export_pdf(resume: ResumeData, output_path: Path) -> Path:
    return build_classic_pdf(resume, output_path)
