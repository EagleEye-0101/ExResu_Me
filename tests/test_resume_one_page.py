from resume_engine.latex.registry import DEFAULT_LATEX_TEMPLATE_ID
from resume_engine.resume_one_page import (
    MAX_EXPERIENCE_ENTRIES,
    fit_resume_one_page,
)
from resume_engine.schemas.resume import Experience, ResumeData


def test_fit_resume_one_page_trims_long_content():
    resume = ResumeData(
        full_name="Test User",
        email="t@example.com",
        phone="5551234567",
        summary="x" * 400,
        experience=[
            Experience(
                company=f"Co {i}",
                title="Engineer",
                start_date="01/2020",
                end_date="Present",
                bullets=[f"Bullet {j} " * 20 for j in range(6)],
            )
            for i in range(6)
        ],
    )
    fitted = fit_resume_one_page(resume)
    assert len(fitted.summary) <= 283
    assert len(fitted.experience) == MAX_EXPERIENCE_ENTRIES
    assert all(len(e.bullets) <= 3 for e in fitted.experience)


def test_default_latex_template_is_compact():
    assert DEFAULT_LATEX_TEMPLATE_ID == "compact"
