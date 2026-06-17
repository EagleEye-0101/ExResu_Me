# Deploy ATS Resume Builder (live links for resume)

Two URLs to share:
- **Web app** (Vercel)
- **API docs** (Render) — `https://<your-api>.onrender.com/docs`

## 1) Deploy API on Render

1. Open https://dashboard.render.com → **New** → **Blueprint**
2. Connect GitHub repo: `EagleEye-0101/ExResu_Me`
3. Render reads [`render.yaml`](render.yaml) automatically
4. When prompted, set **`GEMINI_API_KEY`** (free key: https://aistudio.google.com/apikey)
5. Click **Apply** and wait until service is **Live**
6. Copy API URL, e.g. `https://exresu-me-api.onrender.com`
7. Test: open `https://<api-url>/api/health` and `/docs`

> Free Render services sleep after ~15 min idle. First request may take ~30s to wake.

## 2) Deploy Web on Vercel

1. Open https://vercel.com/new
2. Import GitHub repo: `EagleEye-0101/ExResu_Me`
3. Set **Root Directory** to `web`
4. Add environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://<your-render-api-url>` (no trailing slash)
5. Deploy
6. Open the Vercel URL → click **Try demo resume**

## 3) Wire CORS (after Vercel URL exists)

In Render → **exresu-me-api** → **Environment**:

```
CORS_ORIGINS=http://localhost:3000,https://<your-vercel-app>.vercel.app
```

Save → manual redeploy.

## 4) What to put on resume

```
ATS Resume Builder: https://<vercel-url>
API: https://<render-url>/docs
```

## Local dev (unchanged)

```powershell
cd D:\RESUMEPROJECT
.\.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# other terminal
npm run dev
```

## Notes

- AI generation in cloud uses **Gemini** (set `GEMINI_API_KEY` on Render).
- Ollama is local-only and won't run on Render.
- LaTeX PDF compile needs Tectonic (included in Docker image; optional on Render Python runtime).
