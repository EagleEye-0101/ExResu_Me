import tempfile
from pathlib import Path

import pytest

from resume_engine.export.templates.registry import export_docx, export_pdf
from resume_engine.schemas.resume import Education, Experience, ResumeData, SkillGroup


def _sample() -> ResumeData:
    return ResumeData(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="5551234567",
        github="github.com/jane",
        summary="Full-stack developer with 4 years experience.",
        experience=[
            Experience(
                company="Acme Corp",
                title="Senior Developer",
                location="NYC",
                start_date="01/2022",
                end_date="Present",
                bullets=["Led API redesign", "Mentored 2 juniors"],
            )
        ],
        education=[Education(institution="State University", degree="BS Computer Science", graduation_date="2020")],
        skills=["Python", "React", "SQL", "Docker", "AWS"],
        skill_groups=[
            SkillGroup(label="Languages", skills=["Python", "SQL"]),
            SkillGroup(label="Tools", skills=["React", "Docker", "AWS"]),
        ],
    )


def test_export_docx_differs_by_template():
    resume = _sample()
    with tempfile.TemporaryDirectory() as tmp:
        paths = {}
        for tid in ["professional", "classic", "modern", "compact"]:
            p = Path(tmp) / f"{tid}.docx"
            export_docx(resume, p, tid)
            paths[tid] = p.read_bytes()
        assert paths["professional"] != paths["classic"]
        assert paths["modern"] != paths["classic"]
        assert paths["compact"] != paths["professional"]


def test_export_pdf_with_template():
    resume = _sample()
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "out.pdf"
        export_pdf(resume, p, "professional")
        assert p.exists()
        assert p.stat().st_size > 500
