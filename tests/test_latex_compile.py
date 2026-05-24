import pytest

from resume_engine.latex.compiler import compile_latex, is_latex_available
from resume_engine.latex.demo_data import DEMO_RESUME
from resume_engine.latex.generate import render_resume_latex
from resume_engine.latex.registry import list_latex_templates, resolve_latex_template_id


pytestmark = pytest.mark.skipif(
    not is_latex_available(),
    reason="Tectonic/LaTeX compiler not installed",
)


def test_list_latex_templates_has_four():
    ids = {t["id"] for t in list_latex_templates()}
    assert ids >= {"jake", "alta", "classic", "compact"}


def test_render_demo_source_all_templates():
    for tid in ["jake", "alta", "classic", "compact"]:
        src = render_resume_latex(DEMO_RESUME, tid)
        assert "\\begin{document}" in src
        assert "Alexandra Chen" in src


def test_compile_demo_templates():
    for tid in ["jake", "alta", "classic", "compact"]:
        source = render_resume_latex(DEMO_RESUME, tid)
        result = compile_latex(source)
        assert result.success, f"{tid}: {result.error}\n{result.log}"
        assert result.pdf_bytes is not None
        assert len(result.pdf_bytes) > 5000


def test_resolve_unknown_latex_template():
    assert resolve_latex_template_id("unknown") == "jake"


def test_compile_rejects_shell_escape():
    bad = "\\documentclass{article}\\begin{document}\\write18{rm -rf /}\\end{document}"
    result = compile_latex(bad)
    assert not result.success
    assert result.error
