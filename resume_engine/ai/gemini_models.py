"""Google AI Studio model catalog (verified against Generative Language API)."""

# Free-tier friendly (tested: generateContent OK on typical free keys)
FLASH_MODELS = [
    {"id": "gemini-3-flash-preview", "label": "Gemini 3 Flash (recommended)"},
    {"id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash"},
    {"id": "gemini-flash-latest", "label": "Gemini Flash Latest (auto-updated)"},
    {"id": "gemini-2.5-flash-lite", "label": "Gemini 2.5 Flash Lite (cheapest)"},
    {"id": "gemini-3.1-flash-lite-preview", "label": "Gemini 3.1 Flash Lite Preview"},
]

# High / reasoning tier — often quota-limited on free API keys (429)
HIGH_MODELS = [
    {"id": "gemini-2.5-pro", "label": "Gemini 2.5 Pro (high reasoning)"},
    {"id": "gemini-3.1-pro-preview", "label": "Gemini 3.1 Pro Preview (latest high)"},
    {"id": "gemini-pro-latest", "label": "Gemini Pro Latest (auto-updated high)"},
    {"id": "gemini-3-pro-preview", "label": "Gemini 3 Pro Preview (legacy id)"},
]

DEFAULT_FLASH_MODEL = "gemini-3-flash-preview"
DEFAULT_HIGH_MODEL = "gemini-3.1-pro-preview"

ALL_MODEL_IDS = [m["id"] for m in FLASH_MODELS + HIGH_MODELS]
