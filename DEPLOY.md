# Deploy ATS Resume Builder (live links for resume)

Production URLs:
- **Web app:** https://ex-resu-me.vercel.app
- **API:** https://exresu-me-api.onrender.com
- **API docs:** https://exresu-me-api.onrender.com/docs

## 1) Deploy API on Render (Docker — includes Tectonic for LaTeX)

1. Open https://dashboard.render.com → **New** → **Blueprint**
2. Connect GitHub repo: `EagleEye-0101/ExResu_Me`
3. Render reads [`render.yaml`](render.yaml) automatically (Docker runtime + Tectonic)
4. When prompted, set **`GEMINI_API_KEY`** (free key: https://aistudio.google.com/apikey)
5. Click **Apply** and wait until service is **Live**
6. Copy API URL, e.g. `https://exresu-me-api.onrender.com`
7. Test: open `https://<api-url>/api/health` — expect `"latex_compiler_available": true`

> Free Render services sleep after ~15 min idle. First request may take ~30s to wake.

> SQLite on Render free tier is **ephemeral** — saved resumes reset after redeploys or restarts.

## 2) Deploy Web on Vercel

1. Open https://vercel.com/new
2. Import GitHub repo: `EagleEye-0101/ExResu_Me`
3. Set **Root Directory** to `web`
4. Add environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://exresu-me-api.onrender.com` (no trailing slash)
5. Deploy (redeploy after any env change — Next.js bakes rewrites at build time)
6. Open the Vercel URL → homepage should show hero + hub cards immediately

## 3) Environment variables checklist

### Render → exresu-me-api

| Variable | Value |
|----------|-------|
| `GEMINI_API_KEY` | Your Google AI Studio key (required for AI features) |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000,https://ex-resu-me.vercel.app` |
| `DEFAULT_AI_PROVIDER` | `google_ai_studio` (set in render.yaml) |

Save → manual redeploy after changes.

### Vercel → web project

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://exresu-me-api.onrender.com` |

## 4) Smoke test after deploy

1. `https://ex-resu-me.vercel.app` — hero, LaTeX template cards, and hub cards visible within a few seconds (not stuck on loading)
2. `https://ex-resu-me.vercel.app/api/health` — `status: ok`, `latex_compiler_available: true`
3. `/latex?demo=1` — edit demo resume → **Compile PDF** succeeds
4. `/interview-prep` — upload resume + paste job description → **Google AI Studio** selected → 10 questions generated
5. `/wizard` — create resume with AI generation (needs `GEMINI_API_KEY`)

## 5) What to put on resume

```
ATS Resume Builder: https://ex-resu-me.vercel.app
API: https://exresu-me-api.onrender.com/docs
```

## Local dev (unchanged)

```powershell
cd D:\RESUMEPROJECT
.\.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# other terminal
npm run dev
```

For LaTeX compile locally, install Tectonic once:

```powershell
npm run install:tectonic
```

Verify: `http://127.0.0.1:8000/api/health` → `"latex_compiler_available": true`

## Notes

- AI generation in cloud uses **Gemini** (set `GEMINI_API_KEY` on Render).
- Ollama is local-only and won't run on Render.
- LaTeX PDF compile requires **Docker** deploy on Render (Tectonic is bundled in the [`Dockerfile`](Dockerfile)).
