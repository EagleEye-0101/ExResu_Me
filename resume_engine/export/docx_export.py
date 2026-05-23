from pathlib import Path

from resume_engine.schemas.resume import ResumeData


def export_docx(
    resume: ResumeData, output_path: Path, template_id: str | None = None
) -> Path:
    """Export DOCX using the template registry."""
    from resume_engine.export.templates.registry import export_docx as _export_docx

    return _export_docx(resume, output_path, template_id)
