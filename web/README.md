# Web UI

If you see a **white screen** or styles missing:

```powershell
cd d:\RESUMEPROJECT\web
Remove-Item -Recurse -Force node_modules, .next -ErrorAction SilentlyContinue
npm install
npm run dev
```

Requires the API on port 8000:

```powershell
cd d:\RESUMEPROJECT
.\.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload
```

Open http://localhost:3000
