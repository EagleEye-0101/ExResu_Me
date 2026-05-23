"""Normalize UI / legacy provider ids to keys in PROVIDERS."""

# google_ai_studio → gemini (same API keys; works on all API server versions)
PROVIDER_ALIASES: dict[str, str] = {
    "google_ai_studio": "gemini",
    "google-ai-studio": "gemini",
    "googleaistudio": "gemini",
}


def normalize_provider_id(name: str | None) -> str:
    n = (name or "ollama").strip().lower()
    return PROVIDER_ALIASES.get(n, n)
