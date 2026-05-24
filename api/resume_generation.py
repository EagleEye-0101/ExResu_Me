"""Resume generation entry point used by API routes (always parses AI JSON safely)."""

from __future__ import annotations

from resume_engine.ai.generator import RESUME_JSON_SCHEMA, SYSTEM_PROMPT, _profile_to_prompt
from resume_engine.ai.resume_normalize import parse_ai_resume
from resume_engine.ai.router import get_provider
from resume_engine.schemas.profile import ProfileResponse
from resume_engine.schemas.resume import ResumeData


async def generate_resume_from_profile(
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
