"""Trim resume content so exports target a single letter-sized page."""

from __future__ import annotations

from resume_engine.schemas.resume import (
    Activity,
    Certification,
    Education,
    Experience,
    Project,
    ResumeData,
    SkillGroup,
)

# Tuned for US letter @ ~9–11pt with typical LaTeX templates
MAX_SUMMARY_CHARS = 280
MAX_HEADLINE_CHARS = 72
MAX_EXPERIENCE_ENTRIES = 3
MAX_BULLETS_PER_JOB = 3
MAX_BULLET_CHARS = 115
MAX_EDUCATION_ENTRIES = 2
MAX_PROJECTS = 2
MAX_PROJECT_BULLETS = 2
MAX_ACTIVITIES = 1
MAX_ACTIVITY_BULLETS = 2
MAX_CERTIFICATIONS = 4
MAX_SKILLS_FLAT = 14
MAX_SKILLS_PER_GROUP = 8
MAX_SKILL_GROUPS = 3
MAX_SKILLS_INLINE_CHARS = 200


def _trim_text(text: str, max_len: int) -> str:
    text = (text or "").strip()
    if not text or max_len <= 0:
        return ""
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0]
    return (cut or text[:max_len]).rstrip(".,; ") + "…"


def fit_resume_one_page(resume: ResumeData) -> ResumeData:
    """Return a copy sized to fit one page when rendered with compact/jake-style templates."""
    experience: list[Experience] = []
    for exp in resume.experience[:MAX_EXPERIENCE_ENTRIES]:
        bullets = [_trim_text(b, MAX_BULLET_CHARS) for b in exp.bullets if (b or "").strip()]
        if not bullets:
            bullets = ["Delivered measurable results for the team."]
        experience.append(
            exp.model_copy(update={"bullets": bullets[:MAX_BULLETS_PER_JOB]})
        )

    education = list(resume.education[:MAX_EDUCATION_ENTRIES])

    projects: list[Project] = []
    for proj in resume.projects[:MAX_PROJECTS]:
        bullets = [_trim_text(b, MAX_BULLET_CHARS) for b in proj.bullets if (b or "").strip()]
        projects.append(proj.model_copy(update={"bullets": bullets[:MAX_PROJECT_BULLETS]}))

    activities: list[Activity] = []
    for act in resume.activities[:MAX_ACTIVITIES]:
        bullets = [_trim_text(b, MAX_BULLET_CHARS) for b in act.bullets if (b or "").strip()]
        if bullets:
            activities.append(act.model_copy(update={"bullets": bullets[:MAX_ACTIVITY_BULLETS]}))

    skill_groups: list[SkillGroup] = []
    for g in resume.effective_skill_groups()[:MAX_SKILL_GROUPS]:
        skills = [s.strip() for s in g.skills if s.strip()][:MAX_SKILLS_PER_GROUP]
        if skills:
            skill_groups.append(SkillGroup(label=g.label[:40], skills=skills))

    skills = [s.strip() for s in resume.skills if s.strip()][:MAX_SKILLS_FLAT]
    if not skill_groups and len(skills) > MAX_SKILLS_FLAT:
        skills = skills[:MAX_SKILLS_FLAT]

    certifications = list(resume.certifications[:MAX_CERTIFICATIONS])

    return resume.model_copy(
        update={
            "headline": _trim_text(resume.headline, MAX_HEADLINE_CHARS),
            "summary": _trim_text(resume.summary, MAX_SUMMARY_CHARS),
            "experience": experience,
            "education": education,
            "projects": projects,
            "activities": activities,
            "skill_groups": skill_groups,
            "skills": skills,
            "certifications": certifications,
        }
    )
