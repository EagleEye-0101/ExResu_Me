# ATS Resume Builder

Build ATS-optimized resumes with AI (Ollama local + cloud APIs). Score against job descriptions, fix gaps, and export DOCX/PDF/TXT.

## Features

- **Guided web wizard** — profile, experience, JD, generate, ATS report
- **Weighted ATS score** (0–100) — keyword coverage, structure, parseability, content quality
- **AI providers** — Ollama, OpenAI, Anthropic, Gemini, OpenRouter
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

### 2. Ollama (optional, local AI)

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

### 3. Run API

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Run web UI

```powershell
cd web
npm install
npm run dev
```

Open http://localhost:3000

### 5. CLI examples

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
