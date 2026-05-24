"""Render ResumeData into LaTeX source via Jinja2 templates."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from resume_engine.schemas.resume import ResumeData
from resume_engine.utils.phone import format_phone_display

from resume_engine.latex.registry import resolve_latex_template_id

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _latex_escape(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = text
    for char, repl in replacements.items():
        out = out.replace(char, repl)
    return out


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["tex"] = _latex_escape
    return env


def render_resume_latex(resume: ResumeData, template_id: str | None = None) -> str:
    tid = resolve_latex_template_id(template_id)
    template_name = f"{tid}/resume.tex.j2"
    env = _env()
    tpl = env.get_template(template_name)
    phone = format_phone_display(resume.phone_country_code, resume.phone)
    contact_parts = [
        resume.email,
        phone,
        resume.location,
    ]
    if resume.linkedin:
        contact_parts.append(resume.linkedin)
    if resume.github:
        contact_parts.append(resume.github)
    return tpl.render(
        resume=resume,
        escape=_latex_escape,
        phone=phone,
        contact_line=" $|$ ".join(_latex_escape(p) for p in contact_parts if p),
        skill_groups=resume.effective_skill_groups(),
    )
