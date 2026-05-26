"""LaTeX template gallery registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

LATEX_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = LATEX_ROOT / "templates"

DEFAULT_LATEX_TEMPLATE_ID = "compact"


@dataclass(frozen=True)
class LatexTemplateMeta:
    id: str
    name: str
    description: str
    engine: str
    thumbnail: str


_LATEX_TEMPLATES: dict[str, LatexTemplateMeta] = {
    "jake": LatexTemplateMeta(
        id="jake",
        name="Jake",
        description="Clean one-column layout — ATS-friendly; best with concise content.",
        engine="pdflatex",
        thumbnail="/templates/latex-jake.svg",
    ),
    "alta": LatexTemplateMeta(
        id="alta",
        name="Alta",
        description="Two-column layout — contact, skills, and education in a teal sidebar.",
        engine="pdflatex",
        thumbnail="/templates/latex-alta.svg",
    ),
    "executive": LatexTemplateMeta(
        id="executive",
        name="Executive",
        description="Navy header band with bold name — corporate and leadership roles.",
        engine="pdflatex",
        thumbnail="/templates/latex-executive.svg",
    ),
    "minimal": LatexTemplateMeta(
        id="minimal",
        name="Minimal",
        description="Helvetica-style sans serif, light rules — clean tech and startup look.",
        engine="pdflatex",
        thumbnail="/templates/latex-minimal.svg",
    ),
    "harvard": LatexTemplateMeta(
        id="harvard",
        name="Harvard",
        description="Centered header and small-caps sections — academic and consulting style.",
        engine="pdflatex",
        thumbnail="/templates/latex-harvard.svg",
    ),
    "classic": LatexTemplateMeta(
        id="classic",
        name="Classic",
        description="Traditional serif single-column — formal and readable.",
        engine="pdflatex",
        thumbnail="/templates/latex-classic.svg",
    ),
    "compact": LatexTemplateMeta(
        id="compact",
        name="Compact",
        description="Default one-page layout — tight margins and dense sections (recommended).",
        engine="pdflatex",
        thumbnail="/templates/latex-compact.svg",
    ),
}


def resolve_latex_template_id(template_id: str | None) -> str:
    tid = (template_id or DEFAULT_LATEX_TEMPLATE_ID).strip().lower()
    return tid if tid in _LATEX_TEMPLATES else DEFAULT_LATEX_TEMPLATE_ID


def list_latex_templates() -> list[dict]:
    return [
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "engine": m.engine,
            "thumbnail": m.thumbnail,
            "default": m.id == DEFAULT_LATEX_TEMPLATE_ID,
        }
        for m in _LATEX_TEMPLATES.values()
    ]


def get_template(template_id: str | None) -> LatexTemplateMeta:
    return _LATEX_TEMPLATES[resolve_latex_template_id(template_id)]


def get_demo_source(template_id: str | None = None) -> str:
    from resume_engine.latex.demo_data import DEMO_RESUME
    from resume_engine.latex.generate import render_resume_latex

    return render_resume_latex(DEMO_RESUME, template_id)


def get_template_skeleton(template_id: str | None = None) -> str:
    """Minimal starter for empty editor sessions."""
    tid = resolve_latex_template_id(template_id)
    path = TEMPLATES_DIR / tid / "skeleton.tex"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return get_demo_source(tid)
