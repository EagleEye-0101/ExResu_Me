import json

from resume_engine.ai.router import get_provider
from resume_engine.schemas.resume import ResumeData


async def generate_interview_questions(
    resume: ResumeData,
    job_description: str,
    provider: str | None = None,
    config: dict | None = None,
) -> list[dict]:
    ai = get_provider(provider, config=config)
    messages = [
        {
            "role": "system",
            "content": (
                "Generate 10 likely interview questions for this candidate and role. "
                'Return JSON: {"questions": [{"question": "...", "tip": "..."}]}'
            ),
        },
        {
            "role": "user",
            "content": f"JD:\n{job_description}\n\nResume:\n{resume.to_text()}",
        },
    ]
    raw = await ai.complete(messages, json_schema={"type": "object"})
    if isinstance(raw, dict) and "questions" in raw:
        return raw["questions"]
    return []
