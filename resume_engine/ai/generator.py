import json

from resume_engine.ai.resume_normalize import parse_ai_resume
from resume_engine.ai.router import get_provider
from resume_engine.schemas.profile import EducationInput, ExperienceInput, ProfileResponse
from resume_engine.schemas.resume import ResumeData

SYSTEM_PROMPT = """You are an expert resume writer specializing in ATS-optimized resumes.
Rules:
- Use ONLY facts from the user profile. NEVER invent employers, dates, or credentials.
- Single-column logical structure. No tables, icons, or graphics.
- Bullets: Action verb + quantified metric + outcome. No first person (I/my/we).
- Dates in MM/YYYY format. end_date can be "Present".
- Summary: 2-3 concise lines as a single STRING (not an array).
- Headline should align with the target job when reasonable.
- Skills: include relevant JD keywords that match the candidate's real skills.

Return JSON with these TOP-LEVEL keys only (no personal_information wrapper):
full_name, email, phone, phone_country_code, location, linkedin, github, headline, summary (string),
experience (array), education (array), skills (array of strings),
skill_groups (array of {label, skills}), projects (array), activities (array), certifications (array)."""

RESUME_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "full_name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "phone_country_code": {"type": "string"},
        "location": {"type": "string"},
        "linkedin": {"type": "string"},
        "github": {"type": "string"},
        "headline": {"type": "string"},
        "skill_groups": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "context": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "activities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "summary": {"type": "string"},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "title": {"type": "string"},
                    "location": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["company", "title", "start_date", "bullets"],
            },
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": "string"},
                    "graduation_date": {"type": "string"},
                    "gpa": {"type": "string"},
                },
            },
        },
        "skills": {"type": "array", "items": {"type": "string"}},
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "issuer": {"type": "string"},
                    "date": {"type": "string"},
                },
            },
        },
    },
    "required": ["full_name", "email", "phone", "summary", "experience", "skills"],
}


def _profile_to_prompt(profile: ProfileResponse, job_description: str) -> str:
    profile_dict = profile.model_dump()
    return f"""Create an ATS-optimized resume from this profile and job description.

PROFILE (use only these facts):
{json.dumps(profile_dict, indent=2)}

JOB DESCRIPTION (optimize keywords for this role):
{job_description}

Target role: {profile.target_role or 'Not specified'}
Years of experience: {profile.years_experience}
"""


async def generate_resume(
    profile: ProfileResponse,
    job_description: str,
    provider: str | None = None,
    model: str | None = None,
    config: dict | None = None,
) -> ResumeData:
    ai = get_provider(provider, model, config)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _profile_to_prompt(profile, job_description)},
    ]
    raw = await ai.complete(messages, json_schema=RESUME_JSON_SCHEMA)
    if not isinstance(raw, dict):
        raise ValueError("AI returned non-object JSON; try again or switch model.")
    return parse_ai_resume(raw, profile)


async def optimize_resume(
    resume: ResumeData,
    job_description: str,
    missing_keywords: list[str],
    provider: str | None = None,
    model: str | None = None,
    config: dict | None = None,
) -> ResumeData:
    ai = get_provider(provider, model, config)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""Improve this resume for ATS. Naturally incorporate missing keywords where truthful.
Do not invent experience. Keep single-column ATS format.

MISSING KEYWORDS: {', '.join(missing_keywords[:15])}

JOB DESCRIPTION:
{job_description}

CURRENT RESUME:
{resume.model_dump_json(indent=2)}
""",
        },
    ]
    raw = await ai.complete(messages, json_schema=RESUME_JSON_SCHEMA)
    if not isinstance(raw, dict):
        raise ValueError("AI returned non-object JSON; try again or switch model.")
    return parse_ai_resume(raw, profile_from_resume(resume))


def profile_from_resume(resume: ResumeData) -> ProfileResponse:
    """Minimal profile for normalize fallbacks during optimize."""
    return ProfileResponse(
        id=0,
        full_name=resume.full_name,
        email=resume.email,
        phone=resume.phone,
        phone_country_code=resume.phone_country_code,
        location=resume.location,
        linkedin=resume.linkedin,
        target_role="",
        years_experience=0,
        headline=resume.headline,
        summary_notes=resume.summary,
        experience=[ExperienceInput(**e.model_dump()) for e in resume.experience],
        education=[EducationInput(**e.model_dump()) for e in resume.education],
        skills=list(resume.skills),
        certifications=[c.model_dump() for c in resume.certifications],
    )
