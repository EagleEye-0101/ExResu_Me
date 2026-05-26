"""Template gallery registry (Teal / Resume.io style)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from resume_engine.export.templates import (
    classic,
    compact,
    executive,
    minimal_style,
    modern,
    professional,
)
from resume_engine.schemas.resume import ResumeData

DEFAULT_TEMPLATE_ID = "compact"


@dataclass(frozen=True)
class TemplateMeta:
    id: str
    name: str
    description: str
    thumbnail: str


_TEMPLATES: dict[str, TemplateMeta] = {
    "professional": TemplateMeta(
        id="professional",
        name="Professional",
        description="Labeled contact grid, grouped skills, projects & activities — ATS-friendly.",
        thumbnail="/templates/professional.svg",
    ),
    "classic": TemplateMeta(
        id="classic",
        name="Classic",
        description="Centered header with clean single-column sections.",
        thumbnail="/templates/classic.svg",
    ),
    "modern": TemplateMeta(
        id="modern",
        name="Modern",
        description="Accent bar and bold section headers, still parseable by ATS.",
        thumbnail="/templates/modern.svg",
    ),
    "compact": TemplateMeta(
        id="compact",
        name="Compact",
        description="Tighter spacing for one-page resumes.",
        thumbnail="/templates/compact.svg",
    ),
    "executive": TemplateMeta(
        id="executive",
        name="Executive",
        description="Navy header band — corporate and leadership roles.",
        thumbnail="/templates/executive.svg",
    ),
    "minimal": TemplateMeta(
        id="minimal",
        name="Minimal",
        description="Light sans-serif layout — clean tech and startup style.",
        thumbnail="/templates/minimal.svg",
    ),
}

_RENDERERS: dict[str, Callable[[ResumeData], str]] = {
    "professional": professional.render_html,
    "classic": classic.render_html,
    "modern": modern.render_html,
    "compact": compact.render_html,
    "executive": executive.render_html,
    "minimal": minimal_style.render_html,
}


def resolve_template_id(template_id: str | None) -> str:
    tid = (template_id or DEFAULT_TEMPLATE_ID).strip().lower()
    return tid if tid in _TEMPLATES else DEFAULT_TEMPLATE_ID


def list_templates() -> list[dict]:
    return [
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "thumbnail": m.thumbnail,
        }
        for m in _TEMPLATES.values()
    ]


def get_template(template_id: str | None) -> TemplateMeta:
    return _TEMPLATES[resolve_template_id(template_id)]


def render_resume_html(resume: ResumeData, template_id: str | None = None) -> str:
    from resume_engine.resume_one_page import fit_resume_one_page

    tid = resolve_template_id(template_id)
    return _RENDERERS[tid](fit_resume_one_page(resume))


def export_pdf(resume: ResumeData, output_path: Path, template_id: str | None = None) -> Path:
    from resume_engine.resume_one_page import fit_resume_one_page

    resume = fit_resume_one_page(resume)
    tid = resolve_template_id(template_id)
    if tid == "professional":
        return professional.export_pdf(resume, output_path)
    if tid == "modern":
        return modern.export_pdf(resume, output_path)
    if tid == "compact":
        return compact.export_pdf(resume, output_path)
    if tid == "executive":
        return executive.export_pdf(resume, output_path)
    if tid == "minimal":
        return minimal_style.export_pdf(resume, output_path)
    return classic.export_pdf(resume, output_path)


def export_docx(resume: ResumeData, output_path: Path, template_id: str | None = None) -> Path:
    from resume_engine.resume_one_page import fit_resume_one_page

    resume = fit_resume_one_page(resume)
    tid = resolve_template_id(template_id)
    if tid == "professional":
        return professional.export_docx(resume, output_path)
    if tid == "modern":
        return modern.export_docx(resume, output_path)
    if tid == "compact":
        return compact.export_docx(resume, output_path)
    if tid == "executive":
        return executive.export_docx(resume, output_path)
    if tid == "minimal":
        return minimal_style.export_docx(resume, output_path)
    return classic.export_docx(resume, output_path)
