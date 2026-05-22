from resume_engine.ai.router import get_provider
from resume_engine.schemas.resume import ResumeData


async def generate_cover_letter(
    resume: ResumeData,
    job_description: str,
    provider: str | None = None,
    config: dict | None = None,
) -> str:
    ai = get_provider(provider, config=config)
    messages = [
        {
            "role": "system",
            "content": (
                "Write a professional cover letter. Use only facts from the resume. "
                "3-4 paragraphs, ATS-friendly, no placeholders. Return plain text only."
            ),
        },
        {
            "role": "user",
            "content": f"JOB DESCRIPTION:\n{job_description}\n\nRESUME:\n{resume.to_text()}",
        },
    ]
    result = await ai.complete(messages)
    if isinstance(result, dict) and "letter" in result:
        return result["letter"]
    if isinstance(result, dict) and "content" in result:
        return result["content"]
    return str(result)
