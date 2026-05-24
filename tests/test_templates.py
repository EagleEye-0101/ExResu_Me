from resume_engine.export.templates.registry import list_templates, render_resume_html, resolve_template_id
from resume_engine.schemas.resume import Education, Experience, ResumeData, SkillGroup


def _sample() -> ResumeData:
    return ResumeData(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="5551234567",
        summary="Engineer with 3 years building web apps.",
        experience=[
            Experience(
                company="Acme",
                title="Developer",
                location="NYC",
                start_date="01/2022",
                end_date="Present",
                bullets=["Built APIs"],
            )
        ],
        education=[Education(institution="State U", degree="BS CS", graduation_date="2020")],
        skills=["Python", "React"],
        skill_groups=[SkillGroup(label="Languages", skills=["Python", "TypeScript"])],
    )


def test_list_templates_has_four():
    ids = {t["id"] for t in list_templates()}
    assert ids >= {"professional", "classic", "modern", "compact"}


def test_render_professional_html():
    html = render_resume_html(_sample(), "professional")
    assert "Jane Doe" in html
    assert "Education" in html
    assert "Professional Experience" in html


def test_resolve_unknown_defaults():
    assert resolve_template_id("not-a-template") == "professional"
