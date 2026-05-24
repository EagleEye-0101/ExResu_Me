from resume_engine.ai.router import get_provider


async def coach_bullet(
    bullet: str,
    role: str,
    provider: str | None = None,
    config: dict | None = None,
) -> dict:
    ai = get_provider(provider, config=config)
    messages = [
        {
            "role": "system",
            "content": (
                "Help improve one resume bullet. Ask ONE short question if metrics are missing, "
                'then suggest an improved bullet. Return JSON: {"question": "...", "suggestion": "..."}'
            ),
        },
        {
            "role": "user",
            "content": f"Role: {role}\nBullet: {bullet or '(empty)'}",
        },
    ]
    raw = await ai.complete(messages, json_schema={"type": "object"})
    if isinstance(raw, dict):
        return raw
    return {"question": "What measurable outcome did you achieve?", "suggestion": bullet}
