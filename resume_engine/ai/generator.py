import json

from resume_engine.ai.router import get_provider
from resume_engine.schemas.profile import ProfileResponse
from resume_engine.schemas.resume import ResumeData

SYSTEM_PROMPT = """You are an expert resume writer specializing in ATS-optimized resumes.
Rules:
- Use ONLY facts from the user profile. NEVER invent employers, dates, or credentials.
- Single-column logical structure. No tables, icons, or graphics.
- Bullets: Action verb + quantified metric + outcome. No first person (I/my/we).
- Dates in MM/YYYY format. end_date can be "Present".
- Summary: 2-3 concise lines, human-readable (not keyword soup).
- Headline should align with the target job when reasonable.
- Skills: include relevant JD keywords that match the candidate's real skills.
- Return valid JSON matching the schema exactly."""

RESUME_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "full_name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "phone_country_code": {"type": "string"},
        "location": {"type": "string"},
        "linkedin": {"type": "string"},
        "headline": {"type": "string"},
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
    return ResumeData.model_validate(raw)


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
    return ResumeData.model_validate(raw)
