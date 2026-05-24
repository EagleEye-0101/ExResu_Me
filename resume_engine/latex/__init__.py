"""LaTeX resume compilation and templates."""

from resume_engine.latex.compiler import CompileResult, compile_latex, is_latex_available
from resume_engine.latex.registry import (
    DEFAULT_LATEX_TEMPLATE_ID,
    get_demo_source,
    get_template,
    list_latex_templates,
    resolve_latex_template_id,
)

__all__ = [
    "CompileResult",
    "compile_latex",
    "is_latex_available",
    "DEFAULT_LATEX_TEMPLATE_ID",
    "get_demo_source",
    "get_template",
    "list_latex_templates",
    "resolve_latex_template_id",
]
