from resume_engine.latex.demo_data import DEMO_RESUME
from resume_engine.latex.generate import render_resume_latex
from resume_engine.latex.registry import get_demo_source, list_latex_templates


def test_get_demo_source_contains_all_sections():
    src = get_demo_source("jake")
    assert "Alexandra Chen" in src
    assert "Nimbus Labs" in src
    assert "Certification" in src or "AWS" in src
    assert "OpenMetrics" in src


def test_render_resume_latex_all_templates():
    for tid in [t["id"] for t in list_latex_templates()]:
        out = render_resume_latex(DEMO_RESUME, tid)
        assert "\\documentclass" in out
        assert DEMO_RESUME.full_name in out


def test_list_latex_templates_default():
    templates = list_latex_templates()
    defaults = [t for t in templates if t.get("default")]
    assert len(defaults) == 1
    assert defaults[0]["id"] == "compact"
