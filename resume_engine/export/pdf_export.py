from pathlib import Path

from resume_engine.schemas.resume import ResumeData


def export_pdf(
    resume: ResumeData, output_path: Path, template_id: str | None = None
) -> Path:
    """Export PDF using the template registry."""
    from resume_engine.export.templates.registry import export_pdf as _export_pdf

    return _export_pdf(resume, output_path, template_id)
