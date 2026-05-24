from resume_engine.ai.router import get_provider
from resume_engine.schemas.resume import ResumeData

INTERVIEW_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "tip": {"type": "string"},
                },
                "required": ["question", "tip"],
            },
        },
    },
    "required": ["questions"],
}


def _normalize_questions(raw: list) -> list[dict]:
    out: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        q = (item.get("question") or item.get("q") or "").strip()
        tip = (item.get("tip") or item.get("answer_tip") or item.get("hint") or "").strip()
        if q:
            out.append({"question": q, "tip": tip or "Prepare a concise STAR-format example."})
    return out


async def generate_interview_questions(
    resume: ResumeData,
    job_description: str,
    provider: str | None = None,
    config: dict | None = None,
) -> list[dict]:
    resume_text = resume.to_text()
    if len(resume_text) > 12000:
        resume_text = resume_text[:12000] + "\n...(truncated)"

    jd = (job_description or "General software / professional role").strip()
    if len(jd) > 8000:
        jd = jd[:8000] + "\n...(truncated)"

    ai = get_provider(provider, config=config)
    messages = [
        {
            "role": "system",
            "content": (
                "You are an interview coach. Generate exactly 10 likely interview questions "
                "for this candidate and job. Each item needs a helpful short tip for answering. "
                "Return JSON only."
            ),
        },
        {
            "role": "user",
            "content": f"JOB DESCRIPTION:\n{jd}\n\nRESUME:\n{resume_text}",
        },
    ]
    raw = await ai.complete(messages, json_schema=INTERVIEW_JSON_SCHEMA)
    if isinstance(raw, dict) and "questions" in raw:
        questions = _normalize_questions(raw["questions"])
        if questions:
            return questions[:10]
    raise ValueError(
        "AI returned no interview questions. Check your API key and model in Settings, then try again."
    )
