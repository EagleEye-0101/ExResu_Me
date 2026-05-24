import json
from typing import Protocol

import httpx

from resume_engine.ai.gemini_models import DEFAULT_FLASH_MODEL, FLASH_MODELS, HIGH_MODELS
from resume_engine.config import settings

from resume_engine.ai.provider_ids import normalize_provider_id


def resolve_provider_name(name: str) -> str:
    return normalize_provider_id(name)


class AIProvider(Protocol):
    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        ...


class OllamaProvider:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json" if json_schema else None,
        }
        if json_schema:
            payload["format"] = json_schema

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("message", {}).get("content", "{}")
            return _parse_json(content)


class OpenAIProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if json_schema:
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or "{}"
        return _parse_json(content)


class AnthropicProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        system = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                user_messages.append(m)

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system + ("\nRespond with valid JSON only." if json_schema else ""),
            "messages": user_messages,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["content"][0]["text"]
            return _parse_json(content)


class GeminiProvider:
    """Google AI Studio / Gemini API (https://aistudio.google.com/apikey)."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = (api_key or settings.gemini_api_key).strip()
        self.model = (model or settings.gemini_model).strip()
        if not self.api_key:
            raise ValueError(
                "Google AI Studio API key is required. Create one at https://aistudio.google.com/apikey"
            )

    def _build_request(self, messages: list[dict], json_schema: dict | None) -> dict:
        system_lines: list[str] = []
        contents: list[dict] = []

        for m in messages:
            role = m.get("role", "user")
            text = m.get("content", "")
            if role == "system":
                system_lines.append(text)
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": text}]})
            else:
                contents.append({"role": "user", "parts": [{"text": text}]})

        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Hello"}]}]

        body: dict = {"contents": contents}
        if system_lines:
            instruction = "\n".join(system_lines)
            if json_schema:
                instruction += "\n\nRespond with valid JSON only."
            body["systemInstruction"] = {"parts": [{"text": instruction}]}
        elif json_schema:
            body["systemInstruction"] = {
                "parts": [{"text": "Respond with valid JSON only."}]
            }

        gen_config: dict = {"temperature": 0.3}
        if json_schema:
            gen_config["responseMimeType"] = "application/json"
        body["generationConfig"] = gen_config
        return body

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        model_id = self.model.removeprefix("models/")
        url = f"{self.BASE_URL}/models/{model_id}:generateContent"
        body = self._build_request(messages, json_schema)

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, params={"key": self.api_key}, json=body)
            if not resp.is_success:
                detail = resp.text
                try:
                    err = resp.json()
                    detail = err.get("error", {}).get("message", detail)
                except Exception:
                    pass
                hint = ""
                if resp.status_code == 429:
                    hint = " Try model gemini-3-flash-preview or gemini-2.5-flash in Settings."
                raise ValueError(f"Google AI Studio API error ({resp.status_code}): {detail}{hint}")

            data = resp.json()
            candidates = data.get("candidates") or []
            if not candidates:
                feedback = data.get("promptFeedback", {})
                raise ValueError(
                    f"Google AI Studio returned no content. {feedback or 'Check model name and API key.'}"
                )
            parts = candidates[0].get("content", {}).get("parts") or []
            if not parts:
                raise ValueError("Google AI Studio returned empty response parts.")
            content = parts[0].get("text", "{}")
            return _parse_json(content)


class OpenRouterProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if json_schema:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return _parse_json(content)


def _parse_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        raise


PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "google_ai_studio": GeminiProvider,
    "openrouter": OpenRouterProvider,
}


def get_provider(
    name: str | None = None,
    model: str | None = None,
    config: dict | None = None,
) -> AIProvider:
    cfg = config or {}
    raw_name = (name or cfg.get("default_ai_provider") or settings.default_ai_provider or "").strip()
    canonical = resolve_provider_name(raw_name)
    # Accept both google_ai_studio (UI id) and gemini (canonical)
    lookup = canonical if canonical in PROVIDERS else raw_name.lower()
    if lookup not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {raw_name}. Available: {list_providers_ids()}. "
            "Restart the API server (npm run api) after updating the code."
        )

    cls = PROVIDERS[lookup]
    name = canonical
    if name == "ollama":
        return cls(
            base_url=cfg.get("ollama_base_url") or settings.ollama_base_url,
            model=model or cfg.get("ollama_model") or settings.ollama_model,
        )
    if name == "openai":
        return cls(
            api_key=cfg.get("openai_api_key") or settings.openai_api_key,
            model=model or cfg.get("openai_model") or settings.openai_model,
        )
    if name == "anthropic":
        return cls(
            api_key=cfg.get("anthropic_api_key") or settings.anthropic_api_key,
            model=model or cfg.get("anthropic_model") or settings.anthropic_model,
        )
    if name == "gemini":
        return cls(
            api_key=cfg.get("gemini_api_key") or settings.gemini_api_key,
            model=model or cfg.get("gemini_model") or settings.gemini_model,
        )
    if name == "openrouter":
        return cls(
            api_key=cfg.get("openrouter_api_key") or settings.openrouter_api_key,
            model=model or cfg.get("openrouter_model") or settings.openrouter_model,
        )
    return cls(model=model)


def list_providers_ids() -> list[str]:
    return ["ollama", "google_ai_studio", "openai", "anthropic", "openrouter", "gemini"]


def list_providers() -> list[dict]:
    return [
        {"id": "ollama", "name": "Ollama (Local)", "requires_key": False},
        {
            "id": "google_ai_studio",
            "name": "Google AI Studio (Gemini — free API)",
            "requires_key": True,
            "docs_url": "https://aistudio.google.com/apikey",
            "default_model": DEFAULT_FLASH_MODEL,
            "flash_models": FLASH_MODELS,
            "high_models": HIGH_MODELS,
            "high_tier_note": (
                "Pro / 3.x Pro models often return quota errors on the free API tier. "
                "Use Flash models for free generation, or enable billing in Google AI Studio for Pro."
            ),
        },
        {"id": "openai", "name": "OpenAI", "requires_key": True},
        {"id": "anthropic", "name": "Anthropic", "requires_key": True},
        {
            "id": "gemini",
            "name": "Google Gemini (legacy id)",
            "requires_key": True,
            "docs_url": "https://aistudio.google.com/apikey",
        },
        {"id": "openrouter", "name": "OpenRouter", "requires_key": True},
    ]


async def test_provider(name: str, model: str | None = None, config: dict | None = None) -> dict:
    try:
        provider = get_provider(name, model, config)
        result = await provider.complete(
            [{"role": "user", "content": 'Reply with JSON: {"status": "ok"}'}],
            json_schema={"type": "object"},
        )
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
