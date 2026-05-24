"""Shared helpers for resume templates."""

from __future__ import annotations

import html
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from resume_engine.schemas.resume import ResumeData
from resume_engine.utils.phone import format_phone_display

_TEMPLATES_DIR = Path(__file__).parent / "jinja"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def escape(text: str) -> str:
    return html.escape(text or "")


def phone_display(resume: ResumeData) -> str:
    return format_phone_display(resume.phone_country_code, resume.phone)


def render_jinja(template_name: str, resume: ResumeData, **extra) -> str:
    tpl = _env.get_template(template_name)
    return tpl.render(
        resume=resume,
        escape=escape,
        phone_display=phone_display,
        contact_pairs=contact_pairs,
        **extra,
    )


def contact_pairs(resume: ResumeData) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if resume.github:
        pairs.append(("GitHub", resume.github))
    if resume.email:
        pairs.append(("Email", resume.email))
    if resume.linkedin:
        pairs.append(("LinkedIn", resume.linkedin))
    if resume.phone:
        pairs.append(("Mobile", phone_display(resume)))
    if resume.location and len(pairs) < 4:
        pairs.append(("Location", resume.location))
    return pairs
