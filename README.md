# ATS Resume Builder

Build ATS-optimized resumes with AI (Ollama local + cloud APIs). Score against job descriptions, fix gaps, and export DOCX/PDF/TXT.

## Features

- **Guided web wizard** — profile, experience, JD, generate, ATS report
- **Weighted ATS score** (0–100) — keyword coverage, structure, parseability, content quality
- **AI providers** — Ollama, **Google AI Studio (Gemini, free API)**, OpenAI, Anthropic, OpenRouter
- **Exports** — DOCX (best for ATS), PDF, plain text
- **CLI** — generate, score, optimize, export from terminal
- **Desktop** — Tauri app wrapping the web UI

## Quick start

### 1. Python setup

```powershell
cd d:\RESUMEPROJECT
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
copy .env.example .env
```

Edit `.env` with your API keys and Ollama settings.

### 2. Google AI Studio (free Gemini API, recommended)

1. Open [Google AI Studio](https://aistudio.google.com/apikey) and create an API key.
2. In the app: **Settings → Google AI Studio** — paste the key, set model to `gemini-2.0-flash` (or `gemini-1.5-flash`).
3. Set **Default AI provider** to **Google AI Studio**, save, then **Test Provider**.

Or in `.env`:

```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
DEFAULT_AI_PROVIDER=google_ai_studio
```

### 3. Ollama (optional, local AI)

Install from [ollama.com](https://ollama.com), then:

```powershell
ollama pull llama3.1
```

Set in `.env`:

```
DEFAULT_AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

### 4. Run API

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Run web UI

From the **project root** (installs `web/` deps automatically):

```powershell
cd d:\RESUMEPROJECT
npm install
npm run dev
```

Or only the `web` folder:

```powershell
cd d:\RESUMEPROJECT\web
npm install
npm run dev
```

Open http://localhost:3000

### 6. CLI examples

```powershell
resume init --name "Jane Doe" --email jane@email.com --phone "555-0100" --role "Software Engineer"
resume generate --profile-id 1 --jd .\job_description.txt --provider ollama
resume optimize --resume-id 1 --provider ollama
resume export --resume-id 1 --format docx
resume score resume.json --jd .\job_description.txt
```

### 6. Desktop app

```powershell
cd desktop
npm install
npm run tauri dev
```

## ATS scoring

| Category | Weight |
|----------|--------|
| JD keyword coverage | 35% |
| Section structure | 20% |
| Parseability / format | 25% |
| Content quality | 20% |

Paste the **full job description** for accurate keyword matching. Use **Re-optimize** to inject missing keywords naturally.

## Project structure

```
resume_engine/   # Core: ATS, AI, export, DB
api/             # FastAPI REST
web/             # Next.js UI
cli/             # Typer CLI
desktop/         # Tauri desktop
```

## Environment variables

See [.env.example](.env.example). Never commit `.env` or API keys.

## Docker (optional)

```powershell
docker compose up
```

Includes API + Ollama sidecar.

## Honest limits

- No ATS guarantees a specific score — systems differ (Greenhouse, Workday, etc.)
- AI uses **your profile facts only** — confirm employers/dates in the wizard
- DOCX parses better than PDF for many ATS — export both when unsure
